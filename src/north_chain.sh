#!/bin/bash
cd "d:/PROJECTS/NASA Hackathon/src"
for spec in "7090 -112.47 34.54" "26690 -114.29 34.15" "46289 -114.57 35.13" "34476 -110.03 34.25"; do
  set -- $spec
  python -u opera_download.py --frame $1 --near $2 $3 > ../data/dl_opera_$1.log 2>&1
  python opera_scan.py --frame $1 --name f$1 --min-km2 2 > ../data/scan_$1.log 2>&1
done
echo NORTH_DONE
