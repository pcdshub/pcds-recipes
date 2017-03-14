#!/bin/bash
# Pull out links, then replace the ones that were still needed.
LINKS=$PREFIX/daq-links
$LINKS/uninstall_pyami.sh
for module in "pydaq pycdb"; do
  SCRIPT=$LINKS/install_$module.sh
  if [ -f $SCRIPT ]; then
    $SCRIPT
  fi
done
