import os
import json
import re
from plyfile import PlyData, PlyElement, PlyProperty, PlyListProperty
import numpy as np
import argparse


class TifImg(object):
    def __init__(self, fpath):
        if not os.path.isabs(fpath):
            fpath = os.path.abspath(fpath)
        self.fpath = fpath
        # get metadata of .tif
        meta_str = os.popen('gdalinfo -json {}'.format(self.fpath)).read()
        self.meta = json.loads(meta_str)
        self.size = self.meta['size']  # [width, height]
        # UTM coordinates of image corners
        self.ul = self.meta['cornerCoordinates']['upperLeft'] # [easting, northing]
        self.ur = self.meta['cornerCoordinates']['upperRight']
        self.lr = self.meta['cornerCoordinates']['lowerRight']
        self.ll = self.meta['cornerCoordinates']['lowerLeft']
        # compute pixel resolution
        self.pixel_w = (self.ur[0] - self.ul[0]) / self.size[0]
        self.pixel_h = (self.ul[1] - self.ll[1]) / self.size[1]
        # read the UTM zone
        tmp = self.meta['coordinateSystem']['wkt']
        found = re.search('WGS 84 / UTM zone ([0-9]{1,2})([NS])', tmp)
        self.utm_band = int(found.group(1))
        self.hemisphere = found.group(2)

    def write_meta(self, fname):
        with open(fname, 'w') as fp:
            json.dump(self.meta, fp, indent=2)

    def pixel_coord(self, point):
        (x, y, z) = point

        col = int((x - self.ur[0]) / self.pixel_w)
        row = int((self.ur[1] - y) / self.pixel_h)

        return row, col

    def norm_coord(self, point):
        # the point is in utm coordinate
        # (easting, northing, elevation)
        (x, y, z) = point

        u = (x - self.ll[0]) / (self.lr[0] - self.ll[0])
        v = (y - self.ll[1]) / (self.ul[1] - self.ll[1])

        return u, v


class TextureMapper(object):
    def __init__(self, ply_path, tiff_path):
        self.tiff = TifImg(tiff_path)
        self.ply_data = PlyData.read(ply_path)
        self.vertices = self.ply_data.elements[0]
        self.faces = self.ply_data.elements[1]
        self.ply_textured = None
        self.texture_ply()

    # write texture coordinate to vertex
    def texture_ply(self):
        # drop the RGB properties, and add two new properties (u, v)
        vert_list = []
        for vert in self.vertices.data:
            vert = vert.tolist()   # convert to tuple
            u, v = self.tiff.norm_coord(vert[0:3])
            vert_list.append(vert[0:6]+(u, v))
        vertices = np.array(vert_list,
                            dtype=[('x', '<f4'), ('y', '<f4'), ('z', '<f4'),
                                   ('nx', '<f4'), ('ny', '<f4'), ('nz', '<f4'),
                                   ('u', '<f4'), ('v', '<f4')])
        vert_el = PlyElement.describe(vertices, 'vertex',
                                      comments=['point coordinate, surface normal, texture coordinate'])
        self.ply_textured = PlyData([vert_el, self.faces], text=True)

    # write texture coordinate to face
    @staticmethod
    def insert_uv_to_face(ply_path):
        ply = PlyData.read(ply_path)
        uv_coord = ply['vertex'][['u', 'v']]
        vert_cnt = ply['vertex'].count

        with open(ply_path) as fp:
            all_lines = fp.readlines()
        modified = []
        flag = False; cnt = 0
        for line in all_lines:
            line = line.strip()
            if cnt < vert_cnt:
                modified.append(line)
            if line == 'property list uchar int vertex_indices':
                modified.append('property list uchar float texcoord')
            if flag:
                cnt += 1
            if line == 'end_header':
                flag = True
            if cnt > vert_cnt: # start modify faces
                face = [int(x) for x in line.split(' ')]
                face_vert_cnt = face[0]
                line += ' {}'.format(face_vert_cnt * 2)
                for i in range(1, face_vert_cnt + 1):
                    idx = face[i]
                    line += ' {:.9f} {:.9f}'.format(uv_coord[idx]['u'],  uv_coord[idx]['v'])
                modified.append(line)
        with open(ply_path, 'w') as fp:
            fp.writelines([line + '\n' for line in modified])

    def save(self, fname):
        # convert tiff to jpg
        os.system('gdal_translate -ot Byte -of jpeg {} {}.jpg'.format(self.tiff.fpath, fname))
        # remove the intermediate file
        os.remove(fname + '.jpg.aux.xml')
        # save ply
        name = fname[fname.rfind('/')+1:]
        self.ply_textured.comments = ['TextureFile {}.jpg'.format(name), ]   # add texture file into the comment
        self.ply_textured.write('{}.ply'.format(fname))
        TextureMapper.insert_uv_to_face('{}.ply'.format(fname))


def test():
    print('entering test')
    img = TifImg('/home/kai/satellite_project/sync_folder/true_ortho.tif')
    img.write_meta('true_ortho_meta.json')
    print('all tests passed!')


def test2():
    tiff_path = '/home/kai/satellite_project/sync_folder/true_ortho.tif'
    ply_path = '/home/kai/satellite_project/sync_folder/d2_primitives/001_1_box_color.ply'
    texture_mapper = TextureMapper(ply_path, tiff_path)
    texture_mapper.save('test')


def deploy():
    parser = argparse.ArgumentParser(description='texture-map a .ply to a .tif ')
    parser.add_argument('mesh', help='path/to/.ply/file')
    parser.add_argument('orthophoto', help='path/to/.tif/file')
    parser.add_argument('filename', help='filename for the output files. will output '
                                       '{filename}.ply and {filename}.jpg')
    args = parser.parse_args()

    texture_mapper = TextureMapper(args.mesh, args.orthophoto)
    texture_mapper.save(args.filename)


if __name__ == '__main__':
    # test()
    test2()
    # deploy()