from lxml import etree as ET
import requests
from copy import deepcopy

class McuApiWrapper(object):

    def __init__(self, url, user, pwd, elementTree=None):
        self.url = url
        self.user = user
        self.pwd = pwd
        if elementTree is None:
            self.methodCall = self._baseXML().methodCall
        else:
            self.methodCall = elementTree
  
   
    def _baseXML(self):
        #Clear set method call.
        self.methodCall = ET.Element("methodCall")
        methodName = ET.SubElement(self.methodCall, "methodName")
        params = ET.SubElement(self.methodCall, "params")
        param = ET.SubElement(params, "param")
        value = ET.SubElement(param, "value")
        struct = ET.SubElement(value, "struct")
        creds = (
                self.addMember("authenticationUser", self.user, "string")
                .addMember("authenticationPassword", self.pwd, "string")
        )
        return creds


    def _copy(self, methodCall):
        """Method for duplicating the class"""
        raise NotImplementedError


    def _copyMethodCall(self):
        """Implement tree modification here"""
        copiedET = deepcopy(self.methodCall)
        return copiedET


    def setMethod(self, methodName):
        methodCall = self._copyMethodCall()
        mName = methodCall.find("./methodName")
        mName.text = methodName
        return self._copy(methodCall)
    
    
    def _addMemberBase(self, paramName):
        methodCall = self._copyMethodCall()
        struct = methodCall.find("./params/param/value/struct")

        member = ET.SubElement(struct, "member")
        name = ET.SubElement(member,"name")
        name.text = paramName

        value = ET.SubElement(member, "value")
        return methodCall, value


    def addMember(self, paramName, paramVal, paramType):
        methodCall, value = self._addMemberBase(paramName)
        valType = ET.SubElement(value, paramType)
        valType.text = paramVal
        #print ET.tostring(methodCall)
        #print
        return self._copy(methodCall)


    def addArrMember(self, paramName, paramVals, paramTypes):
        methodCall, value = self._addMemberBase(paramName)
        array = ET.SubElement(value, "array")
        for param, paramType in zip(paramVals, paramTypes):
            data = ET.SubElement(array, "data")
            arrVal = ET.SubElement(data, "value")
            ET.SubElement(arrVal, paramType).text = param
        return self._copy(methodCall)


    def getStrVal(self, xmlTree, paramList):
        op1 = ' or '
        op2 = 'name='
        
        filterParams = op1.join([op2 + "'{}'".format(x) for x in paramList])
        filterStr = ".//member[{}]/value/string".format(filterParams) 
      
        valList = [val.text for val in xmlTree.xpath(filterStr)]

        return valList


    def getArrVal(self, xmlTree, arrParamName, paramName, paramType):
        filterStr = ".//member[name='{}']/value/struct/member[name='{}'] \
                /value/{}".format(arrParamName, paramName, paramType)

        valList = [val.text for val in xmlTree.xpath(filterStr)]

        return valList


    def submitRequest(self, enumId=None):
        """Place HTTP POST Request to the MCU"""
        xml = "<?xml version='1.0' encoding='UTF-8'?>"
        request = xml + ET.tostring(self.methodCall)
        r = requests.post(self.url, data=request)
        #Note: r.content is raw unencoded text
        sanitizedReply = r.content
        #print sanitizedReply
        #self.reset()
        return sanitizedReply
