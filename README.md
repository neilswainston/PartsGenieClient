# PartsGenieClient
PartsGenieClient

To run, call:

`python parts_genie/client.py data/sbol.xml 37762 out`

Updated SBOL documents will be written to the `out` directory.

Alternatively, use Docker as follows:

1. From the Terminal, input `bash docker_build.sh` to build the Docker image.
2. Upon building the image, input `bash docker_run.sh` to run the built image. Parameters are specified withij the `docker_run.sh` file. 