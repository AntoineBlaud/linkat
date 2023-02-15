#/bin/bash
set -x
python3 setup.py install
rm -rf build dist *.egg-info