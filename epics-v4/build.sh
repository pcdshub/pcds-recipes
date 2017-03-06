#!/bin/bash
install -d $PREFIX/bin
install -d $PREFIX/lib
install -d $PREFIX/epics-v4

make -j$(getconf _NPROCESSORS_ONLN)

# Drop everything into the epics-v4 folder
mkdir epics-v4
shopt -s extglob
mv !(epics-v4) epics-v4
shopt -u extglob

# Copy libraries into $PREFIX/lib
PKGS="pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP pvaClientCPP pvDatabaseCPP pvaSrv"
for pkg in $PKGS ; do
  cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*so* $PREFIX/lib 2>/dev/null || : # linux
  cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*dylib* $PREFIX/lib 2>/dev/null || :  # osx
done

# Setup symlinks for utilities
BINS="eget pvget pvinfo pvlist pvput"
cd $PREFIX/bin
for file in $BINS ; do
  ln -s ../epics-v4/pvAccessCPP/bin/$EPICS_HOST_ARCH/$file .
done
