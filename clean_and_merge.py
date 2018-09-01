import argparse
import os

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
        if vert_cnt == 4:
            discard_item_list.append(item)
        else:
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
header[3] = 'element vertex {}\n'.format(len(vert_list))
header[13] = 'element face {}\n'.format(len(face_list))

all_lines = header + vert_list + face_list
with open(output_ply, 'w') as fp:
    fp.writelines(all_lines)

for item in discard_item_list:
    print(item)
print('total numbers of discarded items: {}'.format(len(discard_item_list)))