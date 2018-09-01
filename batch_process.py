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

for item in os.listdir(primitive_folder):
    if item[-4:] == '.ply' and 'box' in item:
        print('processing item: {}'.format(item))
        name = item[:-4]
        texture_mapper = TextureMapper(os.path.join(primitive_folder, item), args.orthophoto)
        texture_mapper.save(os.path.join(output_folder, name))
