#!/bin/bash
install -d $PREFIX/bin
install -d $PREFIX/lib
install -d $PREFIX/epicsv4

make configure
make -j$(getconf _NPROCESSORS_ONLN) pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP
export EPICS4_DIR=`pwd`
export BOOST_PYTHON_DIR=$PREFIX/lib
cd pvaPy
make configure
make

# Copy libraries into $PREFIX/lib
PKGS="pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP"
for pkg in $PKGS ; do
  cp -av $PREFIX/epicsv4/$pkg/lib/$EPICS_HOST_ARCH/lib*so* $PREFIX/lib 2>/dev/null || : # linux
  cp -av $PREFIX/epicsv4/$pkg/lib/$EPICS_HOST_ARCH/lib*dylib* $PREFIX/lib 2>/dev/null || :  # osx
done

# Setup symlinks for utilities
BINS="eget pvget pvinfo pvlist pvput"
cd $PREFIX/bin
for file in $BINS ; do
  ln -s ../epicsv4/bin/$EPICS_HOST_ARCH/$file .
done
