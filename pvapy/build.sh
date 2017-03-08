#!/bin/bash
# Ignore the rest of the EPICS-CPP source and use installed v4
cd pvaPy
export EPICS4_DIR=$EPICS4_BASE

# Manual config because autoconf is broken for python 3
# I can be reasonably sure of the config here because of how conda works
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

# Drop compiled pvaccess.so file into site-packages
cp lib/python/$EPICS_HOST_ARCH/pvaccess.so $PREFIX/lib/python$PY_VER/site-packages
