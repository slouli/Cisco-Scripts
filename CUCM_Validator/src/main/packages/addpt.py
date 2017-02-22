import argparse
from packages.soap import SqlAddPartition

def main(args):
    print("{}, {}".format(args.name, args.description))

    if args.execute:
        print(SqlAddPartition(args.ptName, args.ptDescr).execute())
