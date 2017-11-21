#!/usr/bin/env python3
from packages.soap import GetPhones, DoDeviceLogout
from packages.utilities import getDeviceName
import argparse

def main(office):
    phoneXml=GetPhones(office).execute(True)
    phoneList = getDeviceName(phoneXml)

    logoutRequests = [DoDeviceLogout(device) for (device, _) in phoneList]
    print(logoutRequests)
    #DoDeviceLogout("SEP00082FB62361").execute()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bulk Extension Mobility Logout Tool')
    parser.add_argument('device_pool', type=str)
    args = parser.parse_args()
    main(args.device_pool)
