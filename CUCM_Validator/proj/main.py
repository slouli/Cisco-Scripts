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

    def getPts(self):
        return self.pts

    def getCss(self):
        return self.css


def main():
    
    cssDesign1 = CssPtValidator()
    names = cssDesign1.getPts()
    css = cssDesign1.getCss()

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
    #print(device_pts)
    print("=====================")
    #print(device_css)
    #3. Loop through all the dict entries, confirm the sets are equal
    #   --If not equal, document missing paritions, document extra partitions
    set_diff = {css: device_pts-device_css[css] for css in device_css}

    for key in set_diff:
        print("{} : {}".format(key, set_diff[key])) 


if __name__ == "__main__":
    main()
