#!/bin/bash

TARGET="./submit/***REMOVED***_6/"
ZIP="./submit/***REMOVED***_6.7z"

find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
rm -rf submit
mkdir -p ${TARGET}
cp -r source ${TARGET}
cp -r test ${TARGET}
cp "./***REMOVED***_报告.pdf" ${TARGET}
cp "./***REMOVED***_说明书.pdf" ${TARGET}
cp "./***REMOVED***_演示.mp4" ${TARGET}

7z a -t7z ${ZIP} ${TARGET}