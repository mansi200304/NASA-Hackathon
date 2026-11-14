#!/bin/bash
# wait for each frame's download to finish, then scan it
cd "d:/PROJECTS/NASA Hackathon/src"
for f in 7092 34477 5125 26691; do
  until grep -q "^done" ../data/dl_opera_$f.log 2>/dev/null; do sleep 30; done
  python opera_scan.py --frame $f --name f$f --min-km2 2 > ../data/scan_$f.log 2>&1
done
echo ALL_DONE
