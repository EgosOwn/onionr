#!/bin/bash
cd onionr;
mkdir testdata;
ran=0
for f in tests/*.py; do
  python3 "$f"   || break # if needed 
  let "ran++"
done
rm -rf testdata;
echo "ran $ran test files successfully"