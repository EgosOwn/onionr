#!/bin/bash
cd onionr;
mkdir testdata;
ran=0


close () {
   rm -rf testdata;
   exit 10;
}

for f in tests/*.py; do
  python3 "$f"   || close # if needed 
  let "ran++"
done
rm -rf testdata;
echo "ran $ran test files successfully"