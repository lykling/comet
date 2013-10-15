#!/bin/bash

DIR=$1;
LIST_FILE=/tmp/file.list
find ${DIR} -type f > ${LIST_FILE}
cat ${LIST_FILE} | while read each
do
    #echo ${each};
    if grep -cE "(COFF|PE32|LSB) (relocatable|executable)" <(file "$each") > /dev/null 2>&1
    then
        echo $each;
    fi
done < <(find ${DIR} -type f)
