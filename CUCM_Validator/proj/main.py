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

    def _toString(self):
        return etree.tostring(self.envelope, encoding="UTF-8")


class SqlQuery(SoapBase):

    def __init__(self, query):
        super().__init__()
        self.operation = etree.SubElement(self.body, "{%s}executeSQLQuery" % SoapBase.ns)
        self.operation.set("sequence", "?")
        self.sql = etree.SubElement(self.operation, "sql")
        self.sql.text = query

    def execute(self):
        url="https://10.230.154.5:8443/axl/"
        auth=HTTPBasicAuth(creds.username, creds.password)
        r = requests.post(url, data=self.toString(), auth=auth, verify=False)
        return r.content


    def toString(self):
        return super()._toString()


class CssPtValidator(object):
    
    def __init__(self):
        getPts = "select pkid, name from routepartition"
        getCss = "select name, clause from callingsearchspace"
        xmlPts = etree.fromstring(SqlQuery(getPts).execute())
        xmlCss = etree.fromstring(SqlQuery(getCss).execute())
        self.pts = xmlPts.xpath("//name/text()")
        cssNames = xmlCss.xpath("//name/text()") 
        cssPts = xmlCss.xpath("//clause/text()")
        self.css = {css_name: set(partitions.split(':')) for (css_name, partitions) in zip(cssNames, cssPts)}
        self.ptPat = []
        self._cssPat = ''

    def getPts(self):
        return self.pts

    def getCss(self):
        return self.css

    def addPat(self, string, group=0):
        self.ptPat.append({"pat": string, "group": group})

    @property
    def cssPat(self):
        return self._cssPat

    @cssPat.setter
    def cssPat(self, string):
        self._cssPat = string
    
    def _ptIsValid(self, pat, string, loc):
        is_device = re.search(pat["pat"], string)
        if is_device is None: return False

        if pat["group"] == 1:
            is_same_loc = re.search("PT-(.*)-.*", string).group(1) == loc
            #print('{}, {}, {}'.format(loc, re.search("PT-(.*)-.*", string).group(1), is_same_loc))
            #print('{}, {}, {}'.format(is_same_loc, is_device.group(0), string))
            return (is_same_loc and is_device.group(0) == string)

        return is_device.group(pat["group"]) == string

    def _cssIsValid(self, pat, string):
        is_css= re.search(pat, string)
        return True if is_css else False

    def execute(self):
        css_dict = {css_key: self.css[css_key] for css_key in self.css \
                if self._cssIsValid(self._cssPat, css_key)}
        
        css_loc = [re.match('CSS-(.*)-.*', key).group(1) for key in css_dict]

        for css, loc in zip(css_dict,css_loc):
            pt_set = set([pt for pt in self.pts \
                for pat in self.ptPat \
                if self._ptIsValid(pat, pt, loc)
                ])

            print('===================')
            print(loc)
            print('===================')
            #print(pt_set)
            set_diff_add = pt_set-css_dict[css]

            print("{} : {}".format(css ,set_diff_add))

            set_diff_remove = css_dict[css]-pt_set

            print("{} : {}".format(css, set_diff_remove))
            print()

    def pretty_print(self, set_diff):
        for key in set_diff:
            print("{} : {}".format(key, set_diff[key])) 


def main():
    
    #Instantiate CssPt Validator class, extract partitions and calling search spaces.
    cssDesign1 = CssPtValidator()
    names = cssDesign1.getPts()
    css = cssDesign1.getCss()
   
    cssDesign1.cssPat = 'CSS-.*-Device'
    cssDesign1.addPat('PT-.*-Devices')
    cssDesign1.addPat('PT-General')
    cssDesign1.addPat('Directory URI')
    cssDesign1.addPat('PT-(.*)-Conference', 1)
    cssDesign1.addPat('PT-(.*)-Emergency', 1)
    cssDesign1.execute()

    
    print("NEXT============================================================")

    cssDesign2 = CssPtValidator()
    cssDesign2.cssPat = 'CSS-.*-LocalTF'
    cssDesign2.addPat('PT-(.*)-Devices', 1)
    cssDesign2.addPat('PT-(.*)-LocalTF', 1)
    cssDesign2.addPat('PT-B-National-NA')
    cssDesign2.addPat('PT-B-International-NA')
    cssDesign2.addPat('PT-B-Premium-NA')
    cssDesign2.execute()


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
