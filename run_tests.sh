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
echo "ran $ran unittests. Unittest Time: $SECONDS"
ran=0;

for f in tests/integration-tests/*.py; do
  python3 "$f"   || close # if needed
  let "ran++"
done
echo "ran $ran integration tests."
echo "total test time $SECONDS"
ran=0;

#for f in tests/browser-tests/*.py; do
# python3 "$f"   || close # if needed
# let "ran++"
#done
#echo "ran $ran browser tests."
#echo "total test time $SECONDS"
