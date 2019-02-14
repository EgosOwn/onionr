#!/bin/bash
cd onionr;
mkdir testdata;
for f in tests/*.py; do
  python3 "$f"   || break # if needed 
done
rm -rf testdata;