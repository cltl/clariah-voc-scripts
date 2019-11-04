#!/bin/bash

# adds TEI attributes for parsing the XML file
# and extracts paragraphs 

set -e

in_dir=$1
out_dir=$2
wdir=$(cd $(dirname "${BASH_SOURCE[0]}") && cd .. && pwd)
cd $wdir
temp_dir=$(mktemp -d)

[[ ! -d $out_dir ]] && mkdir -p $out_dir
for f in $in_dir/*; do
  if [ -s $f ]; then
    fname=`basename $f`
    python tei_extracter.py $f $temp_dir/$fname
    sed 's|<TEI>|<?xml version=\"1.0\" encoding=\"UTF-8\"?><TEI xmlns=\"http://www.tei-c.org/ns/1.0\" xmlns:egXML=\"http://www.tei-c.org/ns/Examples\">|' $temp_dir/$fname > $out_dir/$fname
  fi
done

rm -R ${temp_dir}



