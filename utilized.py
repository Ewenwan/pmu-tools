#!/usr/bin/python
# extract utilized CPUs out of toplev CSV output
# toplev ... -I 1000 -x, -o x.csv ...
# utilized.py < x.csv
# note it duplicates the core output
from __future__ import print_function
import argparse
import csv
import sys
import re
import collections

ap = argparse.ArgumentParser()
ap.add_argument('--min-util', default=10., type=float)
args = ap.parse_args()

key = None

c = csv.reader(sys.stdin)
wr = csv.writer(sys.stdout)

fields = dict()
util = collections.defaultdict(list)

for t in c:
    if t[0].startswith("#"):
        continue
    key = t[1] # XXX handle no -I
    if key in fields:
        fields[key].append(t)
    else:
        fields[key] = [t]
    if t[2] == "CPU_Utilization":
        util[t[1]].append(float(t[3]))


final = []
skipped = []
for j in sorted(fields.keys()):
    if "-T" not in j:
        if "S" in j:
            final.append(j)
        continue
    core = re.sub(r'-T%d+', '', j)
    utilization = (sum(util[j]) / len(util[j])) * 100.
    if utilization >= float(args.min_util):
        for k in fields[core] + fields[j]:
            wr.writerow(k)
    else:
        skipped.append(j)
for j in final:
    for k in fields[j]:
        wr.writerow(k)
print("skipped", " ".join(skipped), file=sys.stderr)
