import argparse
from packages.soap import SqlAddPartition
from packages.utilities import getConfirmation

def main(args):
    print("CLuster:{}\nPartition Name:{}\nPartition Description:{}".format(args.cluster, args.name, args.description))

    if args.execute:
        if getConfirmation():
            print(SqlAddPartition(args.cluster, args.name, args.description).execute())
