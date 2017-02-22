import re
import argparse
from lxml import etree
from packages.soap import SqlQuery, SqlAddPartition, SqlAddCss, SqlUpdateCss
from packages.objectify import Location, Css, Partition, PartitionList
from packages.generator import CssDesign, SpecificElement, GenericElement, LocSpecificElement 
from functools import reduce
from utilities import getPartitions, getCallingSearchSpaces, getLocations, partitionFilter, cssFilter


class CssPtValidatorNew(object):
    def __init__(self, name, ptList, cssName, loc = ".*"):
        self.design = [] #List of expected partitions in a CSS
        self.loc = loc #CSS 'location'
        self.func = "" #CSS function (e.g. National)
        
    def addPat(self, loc = ".*", grp=None, conn=None):
        #PT-[ANY]-Devices
        #PT-LOCATION-CONFERENCE
        #PT-LOCATION-EMERGENCY
        #PT-SPECIFICTHING
        paramList = [param for param in [loc, grp, conn] if param is not None]
        pattern = reduce(lambda x, y: x+"-"+y, paramList, "PT")
        self.design.append(pattern)
        print(self.design)


class CssPtValidator(object):
    
    def __init__(self, name, pts, css):
        self.pts = pts
        self.css = css
        self.ptPat = []
        self._cssPat = ''
        self.name = name

    def getPts(self):
        return self.pts

    def getCss(self):
        return self.css

    def addPat(self, string, group=None):
        self.ptPat.append({"pat": string, "group": group})

    @property
    def cssPat(self):
        return self._cssPat

    @cssPat.setter
    def cssPat(self, string):
        self._cssPat = string
    
    def _ptIsValid(self, pat, string, loc):
        is_device = re.search(pat["pat"], string)
        match = re.search("PT-(.*)-.*", string)
        #is_same_loc = 

        #Ignore any strings with no matches and continue
        if is_device is None: return False

        #If the requested pattern had a location, match against that information

        if pat["group"] is not None:
            is_same_loc = re.search("PT-(.*)-.*", string).group(pat["group"]) == loc
            #print('{}, {}, {}'.format(loc, re.search("PT-(.*)-.*", string).group(1), is_same_loc))
            #print('{}, {}, {}'.format(is_same_loc, is_device.group(0), string))
            return (is_same_loc and is_device.group(0) == string)

        #If not, match entire pattern against the string
        return is_device.group(0) == string

    def _cssIsValid(self, pat, string):
        is_css= re.search(pat, string)
        return True if is_css else False

    def execute(self):
        css_dict = {css_key: self.css[css_key] for css_key in self.css \
                if self._cssIsValid(self._cssPat, css_key)}
        
        css_loc = [re.match('CSS-(.*)-.*', key).group(1) for key in css_dict]

        print("\n\n\n==================", 
                self.name,
                "==================\n")
        for css, loc in sorted(zip(css_dict,css_loc)):
            pt_set = set([pt for pt in self.pts \
                for pat in self.ptPat \
                if self._ptIsValid(pat, pt, loc)
                ])

            print('===================\n',
                    loc,
                   '\n===================')

            #print(pt_set)
            set_diff_add = pt_set-css_dict[css]

            print("{} : {}".format("ADD" ,set_diff_add))

            set_diff_remove = css_dict[css]-pt_set

            print("{} : {}\n".format("RMV", set_diff_remove))

    def pretty_print(self, set_diff):
        for key in set_diff:
            print("{} : {}".format(key, set_diff[key])) 


class CssCreator(object):

    def __init__(self, loc, desc, pts, css):
        self.desc = desc
        self.ptList = partitionFilter(pts, "PT-.*-Devices")
        self.cssList = cssFilter(css, "CSS-.*-Device")
        self.ptDeviceName = "PT-{}-Devices".format(loc)
        self.ptDeviceDesc = "PT {} Devices".format(loc)
        self.ptConfName = "PT-{}-Conference".format(loc)
        self.ptConfDesc = "PT {} Global Meet Conferencing".format(loc)
        self.ptEmerName = "PT-{}-Emergency".format(loc)
        self.ptEmerDesc = "PT {} Emergency Calls".format(loc)
        self.cssName = "CSS-{}-Device".format(loc)
        self.cssDesc = "CSS {} Device".format(loc)
    
    def _newPts(self):
        return [SqlAddPartition(self.ptDeviceName, self.ptDeviceDesc), 
                SqlAddPartition(self.ptConfName, self.ptConfDesc), 
                SqlAddPartition(self.ptEmerName, self.ptEmerDesc)]

    def _createCss(self):
        allPts = [self.ptDeviceName, self.ptConfName, self.ptEmerName] + self.ptList
        return SqlAddCss(self.cssName, self.cssDesc, allPts)

    def _updateCss(self):
        return [SqlUpdateCss(cssId, [self.ptDeviceName]) for cssId in self.cssList]

    def validate(self):
        for ptXml in self._newPts(): print(ptXml.toString())
        print(self._createCss().toString())
        for cssUpdate in self._updateCss(): print(cssUpdate.toString())

    def execute(self): pass   #Implement execution of the XML Files


class CssUpdater(object):
    def __init__(self, cssPattern, ptList, css):
        self.cssList = cssFilter(css, cssPattern)
        self.ptList = ptList

    def _updateCss(self):
        return [SqlUpdateCss(cssId, self.ptList + sorted(list(ptSet - set(self.ptList)))) \
                for cssId, ptSet in self.cssList.items()]

    def validate(self):
        for cssUpdate in self._updateCss(): print(cssUpdate.toString())

    def execute(self):
        [print(updateCss.execute()) for updateCss in self._updateCss()]


def main():
    #GET PARTITIONS AND CSS VALUES
    #Can rewrite the query classes as pure AXL vs. AXL with SQL query
    pts = getPartitions()
    css = getCallingSearchSpaces()
    locs = getLocations()

    #Instantiate CssPt Validator class, extract partitions and calling search spaces.
    #Device CSS
    cssDevice = CssPtValidator("Device CSS", pts, css)
    cssDevice.cssPat = 'CSS-.*-Device'
    cssDevice.addPat('PT-.*-Devices')
    cssDevice.addPat('PT-General')
    cssDevice.addPat('Directory URI')
    cssDevice.addPat('PT-(.*)-Conference', 1)
    cssDevice.addPat('PT-(.*)-Emergency', 1)
    cssDevice.addPat('PT-CMS')
    cssDevice.addPat('PT-WLVCS-Outbound')
    cssDevice.addPat('PT-ILS-Trunks')
    cssDevice.addPat('PT-Unity-Pilot')
    cssDevice.addPat('PT-Unity-Ports')
    cssDevice.execute()

    #LocalTF CSS
    cssLocalTF = CssPtValidator("LocalTF CSS", pts, css)
    cssLocalTF.cssPat = 'CSS-.*-LocalTF'
    cssLocalTF.addPat('PT-(.*)-Devices', 1)
    cssLocalTF.addPat('PT-(.*)-LocalTF', 1)
    cssLocalTF.addPat('PT-B-National-NA')
    cssLocalTF.addPat('PT-B-International-NA')
    cssLocalTF.addPat('PT-B-Premium-NA')
    cssLocalTF.execute()

    #National CSS
    cssNational = CssPtValidator("National CSS", pts, css)
    cssNational.cssPat = 'CSS-.*-National'
    cssNational.addPat('PT-(.*)-Devices', 1)
    cssNational.addPat('PT-(.*)-LocalTF', 1)
    cssNational.addPat('PT-(.*)-National', 1)
    cssNational.addPat('PT-B-International-NA')
    cssNational.addPat('PT-B-Premium-NA')
    cssNational.execute()
    
    #International CSS
    cssInternational = CssPtValidator("International CSS", pts, css)
    cssInternational.cssPat = 'CSS-.*-International'
    cssInternational.addPat('PT-(.*)-Devices', 1)
    cssInternational.addPat('PT-(.*)-LocalTF', 1)
    cssInternational.addPat('PT-(.*)-National', 1)
    cssInternational.addPat('PT-(.*)-International', 1)
    cssInternational.addPat('PT-B-Premium-NA')
    cssInternational.execute()


    #Test generic partition filter
    #print(partitionFilter(pts, "PT-.*-Devices"))
    #print(cssFilter(css, "CSS-.*-Device"))
    cssCreatorTest = CssCreator("NEWLOC", "NEWLOC", pts, css)
    cssCreatorTest.validate()

    cssDevice = CssPtValidatorNew("Device CSS", pts, css)
    cssDevice.addPat("CMS")
    cssDevice.addPat("Kingston","Devices")
    cssDevice.addPat(grp="Devices")


    cssDevices = CssDesign("Devices", locs)
    cssDevices.addDesign(SpecificElement("Directory URI"))
    cssDevices.addDesign(SpecificElement("PT-CMS"))
    cssDevices.addDesign(SpecificElement("PT-ILS-Trunks"))
    cssDevices.addDesign(SpecificElement("PT-WLVCS-Outbound"))
    cssDevices.addDesign(SpecificElement("PT-General"))
    cssDevices.addDesign(SpecificElement("PT-Unity-Pilot"))
    cssDevices.addDesign(SpecificElement("PT-Unity-Ports"))
    cssDevices.addDesign(GenericElement("Devices"))
    cssDevices.addDesign(LocSpecificElement("Conference"))
    cssDevices.addDesign(LocSpecificElement("Emergency"))
    for _css in cssDevices.generate(): print(_css)

    ptList = PartitionList.fromStringList(["Directory URI", "PT-CMS", "PT-ILS-Trunks", "PT-WLVCS-Outbound", "PT-Kingston-Devices"])
    videoPts = CssUpdater("CSS-Tampa-Device", ptList.toList(), css)
    videoPts.validate()
    #videoPts.execute()

"""
    #print(css)

    #Convert list to sets
    #0. Define Regular Expressions to define elements in calling search space
    def inDesign(string):
        is_device = re.search('PT-.*-Devices', string)
        return True if is_device else False   
        
    def valid_css(string):
        is_css = re.search('CSS-.*-Device', string)
        return True if is_css else False


    #1. Partition list, convert to set, remove unnecessary partitions for design
    device_pts = set([device_pt for device_pt in names \
            if inDesign(device_pt)
            ])
    
    #2. Remove all dict's that are not devices
    device_css = {device_css: css[device_css] for device_css in css if valid_css(device_css)} 

    print("=====================")
    print("=++++++ADD PTS++++++=")
    print("=====================")
    #print(device_css)
    #3. Loop through all the dict entries, confirm the sets are equal
    #   --If not equal, document missing paritions, document extra partitions
    set_diff = {css: device_pts-device_css[css] for css in device_css}
"""

if __name__ == "__main__":
    main()
