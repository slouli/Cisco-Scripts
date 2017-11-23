#!/usr/bin/env python
import argparse
import re
import pprint
from packages.soap import SqlUpdateCss
from packages.utilities import getPartitions, getCallingSearchSpaces, flatten, partitionFilter, cssFilter, getConfirmation


def main(args):
    pts = getPartitions(args.cluster)
    css = getCallingSearchSpaces(args.cluster)
    
    partitionList = sorted(flatten([partitionFilter(pts, pattern) for pattern in args.members]))
    cssList = cssFilter(css, args.name)
    updatedCss = {cssName:(list(ptList) + list(set(partitionList) - ptList)) for cssName, ptList in cssList.items()}
    
    pprint.pprint(updatedCss)
    
    if args.execute:
        if getConfirmation():
            [print(SqlUpdateCss(args.cluster,cssName, ptList).execute()) for cssName, ptList in updatedCss.items()]


#loc = re.search('CSS-(.*?)-.*', args.name).group(0)
#locs = getLocations()
#for location in locs:
#    ptSubstitute(args.member, "<loc>", location)

#PT-.*-Devices
#PT-<loc>-Conference
#PT-CMS
