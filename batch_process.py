import os
import argparse
from TextureMapper import TextureMapper

parser = argparse.ArgumentParser(description='texture-map all .ply inside a folder to a .tif ')
parser.add_argument('primitive_folder', help='path/to/primitive/folder')
parser.add_argument('orthophoto', help='path/to/.tif/file')
parser.add_argument('output_folder', help='will output .ply and .jpg pairs inside the {output_folder}')
args = parser.parse_args()

primitive_folder = os.path.abspath(args.primitive_folder)
output_folder = os.path.abspath(args.output_folder)
if primitive_folder == output_folder:
    raise ValueError('primitive_folder and output_folder must not be the same')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

flag = True
idx1 = args.orthophoto.rfind('/')
idx2 = args.orthophoto.rfind('.')
texture_fname = os.path.join(output_folder, args.orthophoto[idx1+1:idx2])
for item in os.listdir(primitive_folder):
    if item[-4:] == '.ply':
        print('processing item: {}'.format(item))
        name = item[:-4]
        texture_mapper = TextureMapper(os.path.join(primitive_folder, item), args.orthophoto)
        if flag:    # keep one copy of the texture image
            texture_mapper.save_texture(texture_fname)
            flag = False
        texture_mapper.save_ply(os.path.join(output_folder, name), texture_fname)
