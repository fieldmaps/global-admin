# https://github.com/OSGeo/gdal/tree/master/gdal/docker/ubuntu-full
docker build --build-arg WITH_FILEGDB=true -t fieldmaps/gdal .
