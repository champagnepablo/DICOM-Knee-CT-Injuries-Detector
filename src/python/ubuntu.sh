#!/bin/bash
# Automatically generated script. Based on debpkg.txt.

function apt_install {
  sudo apt-get -y install $1
  if [ $? -ne 0 ]; then
    echo "could not install $1 - abort"
    exit 1
  fi
}

function pip_install {
  for p in $@; do
    sudo pip3 install $p
    if [ $? -ne 0 ]; then
      echo "could not install $p - abort"
      exit 1
    fi
  done
}

function unix_command {
  $@
  if [ $? -ne 0 ]; then
    echo "could not run $@ - abort"
    exit 1
  fi
}

sudo apt-get update --fix-missing

# Minimal installation for a Python ecosystem
# for scientific computing

# Editors
apt_install python3
apt_install libgtk-3-dev
apt_install libopencv-dev python3-opencv
apt_install python3-gi python3-gi-cairo gir1.2-gtk-3.0

pip_install numpy
pip_install opencv-python
pip_install matplotlib
pip_install pydicom


