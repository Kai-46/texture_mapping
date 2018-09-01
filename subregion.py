import os
import argparse
from TextureMapper import TifImg
from plyfile import PlyData
import shutil

parser = argparse.ArgumentParser(description='move primitives in a subregion to a different folder')
parser.add_argument('primitive_folder', help='path/to/primitive/folder')
parser.add_argument('orthophoto', help='path/to/.tif/file')
parser.add_argument('ul_x', type=int, help='pixel coordinate of the subregion\'s upper-left corner')
parser.add_argument('ul_y', type=int, help='pixel coordinate of the subregion\'s upper-left corner')
parser.add_argument('lr_x', type=int, help='pixel coordinate of the subregion\'s lower-right corner')
parser.add_argument('lr_y', type=int, help='pixel coordinate of the subregion\'s lower-right corner')
parser.add_argument('output_folder', help='will move .ply and .jpg pairs into the {output_folder}')
args = parser.parse_args()

primitive_folder = os.path.abspath(args.primitive_folder)
output_folder = os.path.abspath(args.output_folder)
if primitive_folder == output_folder:
    raise ValueError('primitive_folder and output_folder must not be the same')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

tif = TifImg(args.orthophoto)
ul = tif.point_coord((args.ul_x, args.ul_y))
lr = tif.point_coord((args.lr_x, args.lr_y))

for item in os.listdir(primitive_folder):
    if item[-4:] == '.ply' and 'box' in item:
        print('processing item: {}'.format(item))
        ply = PlyData.read(os.path.join(primitive_folder, item))
        x = ply['vertex']['x']
        y = ply['vertex']['y']
        if (ul[0] < x).all() and (x < lr[0]).all() and (lr[1] < y).all() and (y < ul[1]).all():
            shutil.copy(os.path.join(primitive_folder, item),
                        output_folder)
            name = item[:-4]
            shutil.copy(os.path.join(primitive_folder, '{}.jpg'.format(name)),
                        output_folder)