#!/usr/bin/env python
import argparse
import re
import pprint
from packages.soap import SqlAddCss
from packages.utilities import getPartitions, partitionFilter, flatten

def main(args):
    pts = getPartitions()
    partitionList = sorted(flatten([partitionFilter(pts, pattern) for pattern in args.members]))
    pprint.pprint(partitionList)
    
    if args.execute:
        print(SqlAddCss(args.name, args.description, partitionList).execute())

