#!/bin/bash
cd pvaPy
export EPICS4_DIR=$PREFIX/epics-v4

RELEASE="configure/RELEASE.local"
echo "PVACLIENT = $EPICS4_DIR/pvaClientCPP" >> $RELEASE
echo "PVACCESS = $EPICS4_DIR/pvAccessCPP" >> $RELEASE
echo "NORMATIVETYPES = $EPICS4_DIR/normativeTypesCPP" >> $RELEASE
echo "PVDATA = $EPICS4_DIR/pvDataCPP" >> $RELEASE
echo "EPICS_BASE = $EPICS_BASE" >> $RELEASE

SITE="configure/CONFIG_SITE.local"
PYINC="python$PY_VER"
if [ $PY3K ]; then
  USE_M="m"
else
  USE_M=""
fi
echo "PVA_PY_CPPFLAGS = -I$PREFIX/include -I$PREFIX/include/$PYINC$USE_M" >> $SITE
echo "PVA_PY_LDFLAGS = -L/usr/lib64 -L$PREFIX/lib -l$PYINC$USE_M" >> $SITE
echo "PVA_PY_SYS_LIBS = boost_python" >> $SITE
echo "PVA_API_VERSION = 450" >> $SITE
echo "PVA_RPC_API_VERSION = 450" >> $SITE
echo "HAVE_BOOST_NUM_PY = 1" >> $SITE
make

# TODO: get python libraries into site-packages

# # Copy libraries into $PREFIX/lib
# PKGS="pvCommonCPP pvDataCPP pvAccessCPP normativeTypesCPP pvaClientCPP pvDatabaseCPP pvaPy pvaSrv"
# for pkg in $PKGS ; do
#   cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*so* $PREFIX/lib 2>/dev/null || : # linux
#   #cp -av $PREFIX/epics-v4/$pkg/lib/$EPICS_HOST_ARCH/lib*dylib* $PREFIX/lib 2>/dev/null || :  # osx
# done
