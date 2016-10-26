import requests
import re
from requests.auth import HTTPBasicAuth
from lxml import etree
from packages import creds

class SoapBase(object):
    soapenv = "http://schemas.xmlsoap.org/soap/envelope/"
    ns = "http://www.cisco.com/AXL/API/10.0"

    envelope_ns = {
        "soapenv": soapenv,
        "ns": ns
        }

    def __init__(self):
        #Envelope will mutate, must instantiate as part of the object
        self.envelope = etree.Element("{%s}Envelope" % SoapBase.soapenv, nsmap=SoapBase.envelope_ns)
        etree.SubElement(self.envelope, "{%s}Header" % SoapBase.soapenv)
        self.body = etree.SubElement(self.envelope, "{%s}Body" % SoapBase.soapenv)

    def execute(self):
        url="https://10.230.154.5:8443/axl/"
        auth=HTTPBasicAuth(creds.username, creds.password)
        r = requests.post(url, data=self.toString(), auth=auth, verify=False)
        return r.content

    def toString(self):
        return etree.tostring(self.envelope, encoding="UTF-8")


class SqlQuery(SoapBase):

    def __init__(self, query):
        super().__init__()
        self.operation = etree.SubElement(self.body, "{%s}executeSQLQuery" % SoapBase.ns)
        self.operation.set("sequence", "?")
        self.sql = etree.SubElement(self.operation, "sql")
        self.sql.text = query


class SqlAddPartition(SoapBase):
    
    def __init__(self, ptName, ptDesc):
        super().__init__()
        addPt = etree.SubElement(self.body, "{%s}addRoutePartition" % SoapBase.ns)
        addPt.set("sequence", "?")
        pt = etree.SubElement(addPt, "routePartition")
        
        name = etree.SubElement(pt, "name")
        name.text = ptName
        desc = etree.SubElement(pt, "description")
        desc.text= ptDesc


class SqlAddCss(SoapBase):
    
    def __init__(self, cssName, cssDesc, ptList):
        super().__init__()
        addCss = etree.SubElement(self.body, "{%s}addCss" % SoapBase.ns)
        addCss.set("sequence", "?")
        css = etree.SubElement(addCss, "css")
        
        name = etree.SubElement(css, "name")
        name.text = cssName
        desc = etree.SubElement(css, "description")
        desc.text = cssDesc
        members = etree.SubElement(css, "members")
        for idx, pt in enumerate(ptList):
            member = etree.SubElement(members, "member")
            ptName = etree.SubElement(member, "routePartitionName")
            ptName.set("uuid", "?")
            ptName.text = pt
            index = etree.SubElement(member, "index")
            index.text = str(idx)


class SqlUpdateCss(SoapBase):
    
    def __init__(self, cssName, partition):
        super().__init__()
        updateCss = etree.SubElement(self.body, "{%s}updateCss" % SoapBase.ns)
        updateCss.set("sequence", "?")
        name = etree.SubElement(updateCss, "name")
        name.text = cssName

        addMembers = etree.SubElement(updateCss, "addMembers")
        member = etree.SubElement(addMembers, "member")
        ptName = etree.SubElement(member, "routePartitionName")
        ptName.set("uuid", "?")
        ptName.text = partition
        index = etree.SubElement(member, "index")
        index.text = str(0)


def partitionFilter(pts, pattern):
    return [partition for partition in pts if re.search(pattern, partition)]

def cssFilter(css_dict, pattern):
    return {i:css_dict[i] for i in css_dict if re.search(pattern, i)}
            

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
        self.loc = loc
        self.desc = desc
        self.pts = partitionFilter(pts, "PT-.*-Devices")
        self.css = cssFilter(css, "CSS-.*-Device")

    def _newPts(self):
        ptDeviceName = "PT-{}-Devices".format(self.loc)
        ptDeviceDesc = "PT {} Devices".format(self.loc)
        ptConfName = "PT-{}-Conference".format(self.loc)
        ptConfDesc = "PT {} Global Meet Conferencing".format(self.loc)
        ptEmerName = "PT-{}-Emergency".format(self.loc)
        ptEmerDesc = "PT {} Emergency Calls".format(self.loc)
        return [(ptDeviceName, ptDeviceDesc), (ptConfName, ptConfDesc), (ptEmerName, ptEmerDesc)]

    def _createCss(self):
        cssName = "CSS-{}-Device".format(self.loc)
        cssDesc = "CSS {} Device".format(self.loc)
        cssMem = list(self.pts)
        newPts = [pt[0] for pt in self._newPts()]
        cssMem.extend(newPts)    
        return cssName, cssDesc, cssMem

    def _updateOldCss(self): pass

    def validate(self):
        for ptName, ptDescr in self._newPts(): print(SqlAddPartition(ptName, ptDescr).toString())
        cssName, cssDesc, cssMem = self._createCss()
        print(SqlAddCss(cssName, cssDesc, cssMem).toString())

        for cssName in self.css: print(SqlUpdateCss(cssName, "PT-{}-Devices".format(self.loc)).toString())

    def execute(self): pass


def main():
    #GET PARTITIONS AND CSS VALUES
    getPts = "select pkid, name from routepartition"
    getCss = "select name, clause from callingsearchspace"
    xmlPts = etree.fromstring(SqlQuery(getPts).execute())
    xmlCss = etree.fromstring(SqlQuery(getCss).execute())
    pts = xmlPts.xpath("//name/text()")
    cssNames = xmlCss.xpath("//name/text()") 
    cssPts = xmlCss.xpath("//clause/text()")
    css = {css_name: set(partitions.split(':')) for (css_name, partitions) in zip(cssNames, cssPts)}
    

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
