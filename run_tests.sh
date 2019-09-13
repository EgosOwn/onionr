#!/bin/bash
rm -rf testdata;
mkdir testdata;
ran=0

SECONDS=0 ; 
close () {
   rm -rf testdata;
   exit 10;
}

for f in tests/*.py; do
  python3 "$f"   || close # if needed 
  let "ran++"
done
echo "ran $ran test files successfully in $SECONDS seconds"
