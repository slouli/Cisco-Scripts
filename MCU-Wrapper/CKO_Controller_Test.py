import unittest
from lxml import etree as ET
from CKO_Controller import CkoController


class CkoControllerTester(CkoController):
    
    def __init__(self, url='http://fakeurl', user='testUser', pwd='testPass', \
            confName='7760362'):
        super(CkoControllerTester,self).__init__(url, user, pwd, confName)

        """DEFINE TEST XMLS HERE"""

    
    def submitRequest(self, xmlFile=None):
        """Override SubmitRequest Method to Obtain Desired Test Results"""

        reply = open(xmlFile,'r')
        return reply


class CkoControllerTest(unittest.TestCase):

    def test_upper(self):
        """Basic Unit Testing Check"""
        self.assertEqual('foo'.upper(), 'FOO')


    def test_lower(self):
        """Basic Unit Testing Check"""
        self.assertEqual('FOO'.lower(), 'foo')


    def test_baseXML(self):
        """Test Baseline XML for Correctness"""
        appTest = CkoControllerTester()
        methodCall = ET.tostring(appTest._baseXML().methodCall)
        reply = appTest.submitRequest("tests/01-xml_Base.xml").read()
        self.assertEqual(methodCall, reply)


    def test_setMethod(self):
        """Test Setting Method"""
        appTest = CkoControllerTester()
        appTestMethod = appTest.setMethod("participant.enumerate")
        methodCall = ET.tostring(appTestMethod.methodCall)
        reply = appTest.submitRequest("tests/02-xml_setMethod.xml").read()
        self.assertEqual(methodCall, reply)


    def test_addMember(self):
        """Test Adding a Member to MCU_API_Wrapper"""
        appTest = CkoControllerTester()
        appTestMember = (
                appTest.setMethod("participant.enumerate")
                .addMember("enumerateFilter", "(connected)", "string")
                )
        methodCall = ET.tostring(appTestMember.methodCall)
        reply = appTest.submitRequest("tests/03-xml_addMember.xml").read()
        
        
        """EXERCISE: Actual Equivalence Test"""
        self.assertEqual(methodCall, reply) 


#    def test_getParticipantInfo(self):
#        """Ensure all participants are gatehre"""
#        appTest = CkoControllerTester()
#        print appTest.getParticipantInfoRec()
        


if __name__ == '__main__':
    unittest.main()
