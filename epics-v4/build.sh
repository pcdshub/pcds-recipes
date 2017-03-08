#!/bin/bash
install -d $PREFIX/bin
install -d $PREFIX/lib
install -d $PREFIX/epics-v4

# Drop everything into the epics-v4 folder because I don't want to install 10 different directories
cp -R * $PREFIX/epics-v4

# Make in prefix dir so hard-coded paths are fixed correctly
cd $PREFIX/epics-v4
make -j$(getconf _NPROCESSORS_ONLN)

# Copy libraries into $PREFIX/lib
PKGS="pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP pvaClientCPP pvDatabaseCPP pvaSrv"
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
