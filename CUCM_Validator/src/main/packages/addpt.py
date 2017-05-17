import argparse
from packages.soap import SqlAddPartition
from packages.utilities import getConfirmation

def main(args):
    print("{}, {}".format(args.name, args.description))

    if args.execute:
        if getConfirmation():
            print(SqlAddPartition(args.name, args.description).execute())
