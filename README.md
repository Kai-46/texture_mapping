# Simple texture mapping

This codebase implements the texture-mapping a primitive (.ply file) to a ortho-photo (.tif file).

To use on the cluster, simply
* git clone the codebase into the cluster
* then switch to the codebase, and run 'docker build -t \<image name\> .' to build the docker image locally
* then run 'docker_run.sh \<image name\> python /texture_mapping/TextureMapper.py \<mesh file\>
<ortho-photo\> \<output file prefix\>'

Note that 'docker_run.sh' is a script stored at '/phoenix/S3/kz298'

Use 'docker run \<image name\> python /texture_mapping/TextureMapper.py -h' to see the usage details. Or you can use 'docker_run.sh <image name> bash' to enter an interactive bash shell.

'001_1_box_color.ply', 'true_ortho.tif', 'true_ortho_meta.json' are example files from ROI 'wpafb_d2'.