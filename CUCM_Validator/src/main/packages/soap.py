import requests
from packages.creds import Creds, clusters
from requests.auth import HTTPBasicAuth
from lxml import etree

class SoapBase(object):
    """This is the parent class for the XML Soap requests.
    It contains the base XML for all of the UCM directed Soap requests.
    This class should not be instantiated.  Only instantiate it's children"""

    soapenv = "http://schemas.xmlsoap.org/soap/envelope/"
    ns = "http://www.cisco.com/AXL/API/10.0"

    envelope_ns = {
        "soapenv": soapenv,
        "ns": ns
        }

    def _getConfirmation(self):
        """
        confirm = str(input("Are you sure you want to execute [n]: "))
        if confirm is "y" or confirm is "ye" or confirm is "yes": return True
        else: return False
        """
        return True
    
    def __init__(self, cluster):
        self.cluster = clusters(cluster)
        #Envelope will mutate, must instantiate as part of the object
        self.envelope = etree.Element("{%s}Envelope" % SoapBase.soapenv, nsmap=SoapBase.envelope_ns)
        etree.SubElement(self.envelope, "{%s}Header" % SoapBase.soapenv)
        self.body = etree.SubElement(self.envelope, "{%s}Body" % SoapBase.soapenv)

    def execute(self, confirmation = None):
        if confirmation is None: confirmed = self._getConfirmation()
        else: confirmed = confirmation

        if confirmed:
            url="https://{}:8443/axl/".format(self.cluster)
            auth=HTTPBasicAuth(Creds.username, Creds.password)
            r = requests.post(url, data=self.toString(), auth=auth, verify=False)
            return r.content
        else:
            return "Execution Aborted"

    def toString(self):
        return etree.tostring(self.envelope, encoding="UTF-8")

class AddSrst(SoapBase):

    def __init__(self, name, ip, port = "2000",  sipPort = "5060", isSecure = "false"):
        super().__init__()
        addSrst = etree.SubElement(self.body, "{%s}addSrst" % SoapBase.ns)
        addSrst.set("sequence","?")
        srst = etree.SubElement(addSrst, "srst")
        srstName = etree.SubElement(srst, "name")
        srstName.text = name
        srstPort = etree.SubElement(srst, "port")
        srstPort.text = port
        srstIp = etree.SubElement(srst, "ipAddress")
        srstIp.text = ip
        srstSipNetwork = etree.SubElement(srst, "SipNetwork")
        srstSipNetwork.text = ip
        srstSipPort = etree.SubElement(srst, "SipPort")
        srstSipPort.text  
        secure = etree.SubElement(srst, "isSecure")
        srstIsSecure = isSecure
        

class DoDeviceLogout(SoapBase):
    def __init__(self, deviceName):
        super().__init__()
        self.operation = etree.SubElement(self.body, "{%s}doDeviceLogout" % SoapBase.ns)
        self.deviceName = etree.SubElement(self.operation,"deviceName")
        self.deviceName.text = deviceName


class GetPhones(SoapBase):
    def __init__(self, devicePool):
        super().__init__()
        self.operation = etree.SubElement(self.body, "{%s}listPhone" % SoapBase.ns)
        self.searchCriteria = etree.SubElement(self.operation,"searchCriteria")
        self.name = etree.SubElement(self.searchCriteria,"devicePoolName")
        self.name.text = devicePool


class SqlQuery(SoapBase):

    def __init__(self, cluster, query):
        super().__init__(cluster)
        self.operation = etree.SubElement(self.body, "{%s}executeSQLQuery" % SoapBase.ns)
        self.operation.set("sequence", "?")
        self.sql = etree.SubElement(self.operation, "sql")
        self.sql.text = query


class SqlAddPartition(SoapBase):
    
    def __init__(self, cluster, ptName, ptDesc):
        super().__init__(cluster)
        addPt = etree.SubElement(self.body, "{%s}addRoutePartition" % SoapBase.ns)
        addPt.set("sequence", "?")
        pt = etree.SubElement(addPt, "routePartition")
        
        name = etree.SubElement(pt, "name")
        name.text = ptName
        desc = etree.SubElement(pt, "description")
        desc.text= ptDesc


class SqlAddCss(SoapBase):
    
    def __init__(self, cluster, cssName, cssDesc, ptList):
        super().__init__(cluster)
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


class SqlGetCss(SoapBase):
    def __init__(self, cluster, cssName):
        super().__init__(cluster)
        getCss = etree.SubElement(self.body, "{$s}getCss" % SoapBase.ns)
        getCss.set("sequence", "?")
        name = etree.SubElement(getCss, "name")
        name.text = cssName


class SqlUpdatePt(SoapBase):
    def __init__(self, cluster, ptName, newPtName):
        super().__init__(cluster)
        updatePt = etree.SubElement(self.body, "{%s}updateRoutePartition" % SoapBase.ns)
        updatePt.set("sequence", "?")
        name = etree.SubElement(updatePt, "name")
        name.text = ptName
        newName = etree.SubElement(updatePt, "newName")
        newName.text = newPtName


class SqlUpdateCss(SoapBase):
    
    def __init__(self, cluster, cssName, ptList):
        super().__init__(cluster)
        updateCss = etree.SubElement(self.body, "{%s}updateCss" % SoapBase.ns)
        updateCss.set("sequence", "?")
        name = etree.SubElement(updateCss, "name")
        name.text = cssName
        addMembers = etree.SubElement(updateCss, "members")
        
        for idx, pt in enumerate(ptList):
            member = etree.SubElement(addMembers, "member")
            ptName = etree.SubElement(member, "routePartitionName")
            ptName.set("uuid", "?")
            ptName.text = pt
            index = etree.SubElement(member, "index")
            index.text = str(idx)
