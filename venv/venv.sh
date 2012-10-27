#!/bin/bash

virtualenv --no-site-packages .
pip install -r requirements
source bin/activate
PYTHONPATH=$PYTHONPATH:`pwd`/..; export PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"
