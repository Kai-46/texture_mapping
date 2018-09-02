# Simple texture mapping

This codebase implements texture-mapping a primitive (.ply file) to a ortho-photo (.tif file).

To use on the phoenix cluster, simply
* git clone the codebase into the cluster
* then switch to the codebase directory, and run 'docker build -t \<image name\> .' to build a docker image locally
* then run './docker_run.sh \<image name\> python TextureMapper.py \<mesh file\> <ortho-photo\> \<output filename\>'

Note that 'output filename' should not include the file extension, as the the program will output a pair of files, i.e., '{output filename}.ply' and '{output filename}.jpg'. The script 'docker_run.sh' starts a container with cluster directory ‘/phoenix/’ mounted, and the same user id as that on the cluster.

Use 'docker run \<image name\> python TextureMapper.py -h' to see the usage details. Or you can use './docker_run.sh -ti \<image name\> bash' to enter an interactive bash shell. Note that non-root user (user id != 0) only has access to the working directory '/texture_mapping/' on the container filesystem. 

In the folder 'example_data/', '001_1_box_color.ply', 'true_ortho.tif', 'true_ortho_meta.json' are example files from ROI 'd2_wpafb'. 'true_ortho_meta.json' is the metadata extracted from 'true_ortho.tif'.

Example usages:
* ./docker_run.sh \<image name\> python TextureMapper.py example_data/001_1_box_color.ply example_data/true_ortho.tif 001_1_box_color
  * the program will output '/texture_mapping/001_1_box_color.ply' and '/texture_mapping/001_1_box_color.jpg' to the container filesystem. The output '.ply' is the textured mesh, with '.jpg' being the texture image. To make the output files persistent, one should specify a directory inside the mounted host volume '/phoenix/'.
  * you can use [Meshlab](http://www.meshlab.net/) or [CloudCompare](https://www.danielgm.net/cc/) to visualize the textured mesh. Recommended software is CloudCompare.

It seems that these visualization tools are not good at handling hundreds of small .ply files at a time. So for convenience, we also provide the utility 'merge.py' to merge all the primitives into a single .ply file. Use 'docker_run.sh \<image name\> python merge.py \<primitive_folder\>  \<output_ply_name\>'.

Example usage:
* ./docker_run.sh \<image name\> python merge.py /path/to/d2_primitves/ d2_merged.ply
  * the program will output '/texture_mapping/d2_merged.ply' to the container filesystem. Since 'box_color.ply' files have colored vertices and also have surface normals, while 'nonBox.ply' files do not, therefore, we discard the vertex color and surface normal in order to merge all the '.ply' files.
  * to texture-map the merged '.ply' file, use the command mentioned before.

The recommended workflow is: first merge all the primitives into a single '.ply' file, then texture-map the merged file, and finally visualize the textured mesh in CloudCompare.

To batch-process the texture-mapping of all the primitives in a folder, use
'./docker_run.sh \<image name\> python batch_process.py \<primitive_folder\> <ortho-photo\> \<output_folder\>'
