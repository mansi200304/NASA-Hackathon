#!/bin/bash
cd "d:/PROJECTS/NASA Hackathon/src"
for spec in "7091 central" "34478 southeast" "34477 f34477" "7092 f7092" "5125 f5125"; do
  set -- $spec; python opera_scan.py --frame $1 --name $2 --min-km2 2 > ../data/rescan_$1.log 2>&1
done
echo RESCAN_DONE
