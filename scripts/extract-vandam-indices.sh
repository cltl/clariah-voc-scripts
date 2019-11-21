#!/bin/bash

# vandam index files are presorted by volume and label:
# .../1-I/PER
# we read the volume from $indir and the labels from its subfolders

indir=$1
outdir=$2
[[ ! -d $outdir ]] && mkdir -p $outdir
 
volume=`basename $indir`
workdir=$(cd $(dirname "${BASH_SOURCE[0]}") && cd .. && pwd)

for labeldir in $indir/*; do
  label=`basename $labeldir`
  python html_vandam_indices.py $volume $labeldir $label $outdir/indices_${volume}_${label}.txt
done

cat $outdir/indices_${volume}_*.txt > $outdir/indices_${volume}.txt
