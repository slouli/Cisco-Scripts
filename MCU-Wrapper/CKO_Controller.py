from lxml import etree as ET
import requests
from MCU_API_Wrapper import McuApiWrapper
from creds import *

class CkoController(McuApiWrapper):

    def __init__(self, url, user, pwd, confName, elementTree=None):
        
        self.confName = confName
        super(CkoController,self).__init__(url, user, pwd, elementTree)
        
        #self.participantList = list()
        #self.reset()
        return


    def _copy(self, methodCall):
        return CkoController(self.url, self.user, self.pwd, self.confName, \
                methodCall)


    def getParticipantInfoRec(self):
        """Recursively get participant information from conference confName"""

        def _getParticipantInfoRec(self, _enumId, _dNameList, _pNameList, \
                _pTypeList, _confNameList, _pMutedList, _pImportantList):

            if not _enumId:
                enumMethodCall = ""
            else:
                enumMethodCall = _enumId.pop()
                print enumMethodCall

            methodCall = (
                    self.setMethod("participant.enumerate")
                    .addArrMember("operationScope", ["currentState"],["string"])
                    .addMember("enumerateFilter", "(connected)", "string")
                    .addMember("enumerateID", enumMethodCall, "string")
                    )

            root = ET.fromstring(methodCall.submitRequest())
            enumId = self.getStrVal(root, ["enumerateID"])
            dNameList = _dNameList + self.getStrVal(root, ["displayName"])
            pNameList = _pNameList + self.getStrVal(root, ["participantName"])
            pTypeList = _pTypeList + self.getStrVal(root, ["participantType"])
            
            confNameList = _confNameList + self.getStrVal(
                    root, ["conferenceName", "autoAttendantUniqueId"]
                    )
        
            pMutedList = _pMutedList + self.getArrVal(
                    root, "currentState", "audioRxMuted", "boolean"
                    )

            pImportantList = _pImportantList + self.getArrVal(
                    root, "currentState", "important", "boolean"
                    )

            #print pNameList
            #print dNameList
            #print pTypeList
            #print confNameList

            if not enumId:
                pList = [(dName, pName, pMuted, pImportant, pType, confName) \
                        for (dName, pName, pMuted, pImportant, pType, confName)\
                        in zip(dNameList, pNameList, pMutedList, \
                        pImportantList, pTypeList, confNameList) \
                        if confName == self.confName]
                return pList

            else:
                return _getParticipantInfoRec(self, enumId, dNameList, pNameList, \
                        pTypeList, confNameList, pMutedList, pImportantList)
        
        return _getParticipantInfoRec(self, [], [], [], [], [], [], [])


    def getParticipantInfo(self):

        enumId = []
        dNameList = []
        pNameList = []
        pTypeList = []
        confNameList = []
        pMutedList = []
        pImportantList = []

        while True:
            self.setMethod("participant.enumerate")
            self.addArrMember("operationScope", ['currentState'])
            self.addMember("enumerateFilter", "(connected)", "string")

            #Check if enumId is set
            self.addMember("enumerateID", "" if not enumId else enumId.pop(), "string")

            root = ET.fromstring(self.submitRequest())
            
            enumId = self.getStrVal(root, ["enumerateID"])
            dNameList = dNameList + self.getStrVal(root, ["displayName"])
            pNameList = pNameList + self.getStrVal(root, ["participantName"])
            pTypeList = pTypeList + self.getStrVal(root, ["participantType"])
            confNameList = confNameList + self.getStrVal(root, ["conferenceName", "autoAttendantUniqueId"])
        
            pMutedList = pMutedList + self.getArrVal(root, "currentState", "audioRxMuted", "boolean")
            pImportantList = pImportantList + self.getArrVal(root, "currentState", "important", "boolean")
            
            self.participantList = [(dName, pName, pMuted, pImportant, pType, confName) for (dName, pName, pMuted, pImportant, pType, confName) in zip(dNameList, pNameList, pMutedList, pImportantList, pTypeList, confNameList) if confName == self.confName] 
             
            #If there are no more returned IDs, we have checked all participants
            if not enumId:
                break
        return


    def _sendMsg(self, confName, pId, pProtocol, pType, msg):
        methodCall = (
                self.setMethod("participant.message")
                .addMember("conferenceName", confName, "string")
                .addMember("participantName", pId, "string")
                .addMember("participantProtocol", "sip", "string")
                .addMember("participantType", pType, "string")
                .addMember("message", msg, "string")
                .addMember("durationSeconds", "10", "int")
                .addMember("verticalPosition", "top", "string")
                )
                                        
        result = methodCall.submitRequest() 
        return 

 
    def modifyParticipant(self, confName, pList, userIndex):
        """Mute Participant or Unmute and set as Important"""
        (pName, pId, pMuted, pImportant, pType, confNum) = pList[int(userIndex)]
        
        impVal = "0" if pMuted == "0" else "1"
        mutedVal = "1" if pMuted == "0" else "0"
        visualCue = "You Are Live!" if mutedVal == "0" else "You Are Muted"       
        methodCall = (
                self.setMethod("participant.modify")
                .addMember("conferenceName", confName, "string")
                .addMember("participantName", pId, "string")
                .addMember("participantProtocol", "sip", "string")
                .addMember("participantType", pType, "string")
                .addMember("operationScope", "activeState", "string")
                .addMember("important", impVal, "boolean")
                .addMember("audioRxMuted", mutedVal, "boolean")
                )

        ret = methodCall.submitRequest()

        self._sendMsg(confName, pId, "sip", pType, visualCue)
        return


    def prettyPrint(self, pList):
        """Display User Information to the cmd Prompt"""
        print "\n=====AVAILABLE ACTIONS=====\n"
        for eid, (pName, pId, pMuted, pImportant, pType, confNum) in enumerate(pList):
            impFlag = " " if pImportant == "0" else "*"
            muteFlag = "Mute" if pMuted == "0" else "Unmute"

            print "{}{}. {}: {}, {}, {}, {}".format(impFlag, eid, muteFlag, pName, pId, pType, confNum) 
        return


def main():
    
    confApp = CkoController(url, user, pwd, confName)
   
    while(True):
        
        pList = confApp.getParticipantInfoRec()
        confApp.prettyPrint(pList)

        print

        selectedParticipant = raw_input("Select participant: ")
        
        try:
            confApp.modifyParticipant(confName, pList, selectedParticipant)
        except ValueError:
            print "Invalid value entry, refreshing participant list..."
            continue
        except IndexError:
            print "Index was out of bounds, refreshing participant list..."
            continue


if __name__ == "__main__":
    main()
