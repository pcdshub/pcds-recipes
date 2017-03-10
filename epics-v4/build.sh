#!/bin/bash
install -d $PREFIX/bin
install -d $PREFIX/lib
install -d $PREFIX/epics-v4

# Install copy of the perl tool so the comment makes sense
cp -R tools $PREFIX/epics-v4

PKGS="pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP pvaClientCPP pvDatabaseCPP pvaSrv"

# Create RELEASE.local in each configure directory to link dependencies
# Do in both build directory and install directory
for pkg in $PKGS ; do
  mkdir -p $PREFIX/epics-v4/$pkg/configure
  echo "$pkg=$PREFIX/epics-v4/$pkg" >> "$pkg/configure/RELEASE.local"
  echo "$pkg=$PREFIX/epics-v4/$pkg" >> "$PREFIX/epics-v4/$pkg/configure/RELEASE.local"
done

make -j$(getconf _NPROCESSORS_ONLN)

# Copy libraries into $PREFIX/lib
for pkg in $PKGS ; do
  cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*so* $PREFIX/lib 2>/dev/null || : # linux
  cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*dylib* $PREFIX/lib 2>/dev/null || :  # osx
done

# Setup symlinks for utilities
BINS="eget pvget pvinfo pvlist pvput"
for file in $BINS ; do
  ln -s $PREFIX/epics-v4/pvAccessCPP/bin/$EPICS_HOST_ARCH/$file $PREFIX/bin
done

# deal with env export
# this isn't standard like EPICS_BASE is, but it's useful for building pvaPy
mkdir -p $PREFIX/etc/conda/activate.d
mkdir -p $PREFIX/etc/conda/deactivate.d

ACTIVATE=$PREFIX/etc/conda/activate.d/epics_v4.sh
DEACTIVATE=$PREFIX/etc/conda/deactivate.d/epics_v4.sh

# set up
echo "export EPICS4_BASE=$PREFIX/epics-v4" >> $ACTIVATE

# tear down
echo "unset EPICS4_BASE" >> $DEACTIVATE

# make sure activate and deactivate scripts have exec permissions
chmod a+x $ACTIVATE
chmod a+x $DEACTIVATE

# clean up after self
unset ACTIVATE
unset DEACTIVATE
