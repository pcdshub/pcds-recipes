#!/bin/bash
# Hutch environment variable needs to be set
set -u
: $HUTCH

# For the daq modules, we need to sym-link to the libraries in current...
# This is because the modules need to be synced to the active daq version
#   on a per-hutch basis.
# As a programmer, this makes me sad. We'll pretend like it's ok.

LIB="$PREFIX/lib"
SITE_PACKAGES="$LIB/python$PY_VER/site-packages"
install -d $SITE_PACKAGES

if [[ "$(uname -r)" =~ "el7" ]]; then
  ARCH="x86_64-rhel7-opt"
else
  ARCH="x86_64-linux-opt"
fi

installdir(){
  FULLDIR="$1"
  FILTER="$2"

  FILES="$(ls -U1 $FULLDIR)"
  for file in $FILES
  do
    if [[ (-z "$FILTER") || ($file =~ "$FILTER") ]]; then
      if [[ $file =~ "lib" ]]; then
        DEST="$LIB/$file"
      elif [[ $file =~ ".so" ]]; then
        DEST="$SITE_PACKAGES/$file"
      else
        DEST=""
      fi
      if [[ !(-z $DEST) && !(-e $DEST) ]]; then
        ln -s $FULLDIR/$file $DEST
      fi
    fi
  done
}

# Defer to daq versions of the libraries over ami versions
DAQ="/reg/g/pcds/dist/pds/$HUTCH/current/build"
for libdir in pdsapp psalg pds pdsdata offlinedb
do
  installdir "$DAQ/$libdir/lib/$ARCH"
done

AMI="/reg/g/pcds/dist/pds/$HUTCH/ami-current/build"
for libdir in ami gsl qt
do
  installdir "$AMI/$libdir/lib/$ARCH"
done

unset HUTCH
unset LIB
unset SITE_PACKAGES
unset ARCH
unset DAQ
unset AMI
