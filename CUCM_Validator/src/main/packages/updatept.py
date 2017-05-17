#!/usr/bin/env python
import argparse
import pprint
from packages.utilities import getPartitions, ptSubstitute, partitionFilter, getConfirmation
from packages.soap import SqlUpdatePt

def main(args):
    pts = getPartitions()
    filteredPts = partitionFilter(pts, args.pattern)
    ptDict = ptSubstitute(filteredPts, args.match, args.replace)
    pprint.pprint(ptDict)
    
    if args.execute:
        if getConfirmation():
            [print(SqlUpdatePt(oldName, newName).execute()) for oldName, newName in ptDict.items()]

