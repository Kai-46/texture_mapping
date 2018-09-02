import argparse
import os
from plyfile import PlyData

parser = argparse.ArgumentParser(description='merge multiple .ply files representing primitives into a single one')
parser.add_argument('primitive_folder', help='path/to/primitive/folder')
parser.add_argument('output_ply', help='path/to/output/ply')

args = parser.parse_args()
primitive_folder = args.primitive_folder
output_ply = args.output_ply

if not os.path.isabs(primitive_folder):
    primitive_folder = os.path.abspath(primitive_folder)

if not os.path.isabs(output_ply):
    output_ply = os.path.abspath(output_ply)

item_list = os.listdir(primitive_folder)

discard_item_list = []
vert_list = []
face_list = []
index_drift = 0
for item in item_list:
    if item[-4:] == '.ply' and 'box_color' in item:
        with open(os.path.join(primitive_folder, item)) as fp:
            all_lines = fp.readlines()
        vert_cnt = int(all_lines[3].strip().split(' ')[2])
        face_cnt = int(all_lines[13].strip().split(' ')[2])

        vert_list.extend(all_lines[16:16+vert_cnt])
        # need to modify vertex index
        faces = all_lines[16+vert_cnt:16+vert_cnt+face_cnt]
        for i in range(face_cnt):
            tmp = [int(x) for x in faces[i].strip().split(' ')]
            faces[i] = '3 {} {} {}\n'.format(tmp[1] + index_drift,
                                             tmp[2] + index_drift, tmp[3] + index_drift)
        face_list.extend(faces)
        index_drift += vert_cnt
    else:
        discard_item_list.append(item)

header = all_lines[:16]

# now start to merge the 'nonBox.ply' files
header = header[:7] + header[13:]
another_vert_list = []
for vert in vert_list:
    tmp = vert.strip().split(' ')
    another_vert_list.append('{} {} {}\n'.format(tmp[0], tmp[1], tmp[2]))

for item in discard_item_list:
    if 'nonBox' in item:
        ply = PlyData.read(os.path.join(primitive_folder, item))
        for vert in ply['vertex']:
            another_vert_list.append('{} {} {}\n'.format(vert['x'], vert['y'], vert['z']))
        for face in ply['face']:
            face = face[0]
            if len(face) != 3:
                raise ValueError('non-triangular mesh detected: {}'.format(item))
            else:
                face_list.append('3 {} {} {}\n'.format(face[0]+index_drift,
                                                       face[1]+index_drift, face[2]+index_drift))
        index_drift += ply['vertex'].count

header[3] = 'element vertex {}\n'.format(len(another_vert_list))
header[7] = 'element face {}\n'.format(len(face_list))
all_lines = header + another_vert_list + face_list

with open(output_ply, 'w') as fp:
    fp.writelines(all_lines)
