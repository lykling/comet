#!/bin/sh

ver=(109634 109906 110062 110115 110347 110541)
file=$1;

for i in {1..6}
do
    old=${ver[$((i-1))]};
    new=${ver[$i]};
    svn diff -r${old}:${new} $file > ${old}-${new}.diff;
done;
