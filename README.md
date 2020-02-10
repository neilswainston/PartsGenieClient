# PartsGenieClient
PartsGenieClient

To run, call:

`python parts_genie/client.py data/sbol_rbs.xml 37762 out`

Updated SBOL documents will be written to the `out` directory.

Alternatively, use Docker as follows:

1. From the Terminal, input `bash docker_build.sh` to build the Docker image.
2. Upon building the image, input `bash docker_run.sh` to run the built image. Parameters are specified within the `docker_run.sh` file. Specifically, these are:
    * `https://parts.synbiochem.co.uk/` The URL of the PartsGenie instance.
    * `/data/sbol_rbs.xml` The input file.
    * `37762` The NCBI taxonomy id of the target host organism.
    * `/out` The output directory.