#!/usr/bin/env python
import argparse
import re
import pprint
from packages.soap import SqlAddCss
from packages.utilities import getPartitions, partitionFilter, getConfirmation, flatten

def main(args):
    pts = getPartitions(args.cluster)
    partitionList = sorted(flatten([partitionFilter(pts, pattern) for pattern in args.members]))
    print("CSS Cluster: {}\nCSS Name: {}\nCSS Description: {}".format(args.cluster, args.name, args.description))
    print("CSS Members:")
    pprint.pprint(partitionList)
    
    if args.execute:
        if getConfirmation():
            print(SqlAddCss(args.cluster,args.name, args.description, partitionList).execute())

