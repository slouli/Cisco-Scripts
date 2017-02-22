from packages.objectify import LocationList, Css, Partition
from packages.utilites import flatten
from functools import reduce

class CssDesign(object):

    def __init__(self, designName, locList):
        self.locList = locList
        self.designList = []
        self.cssList = [] #List of CSS objects

    def generate(self):
        """For every location, construct CSS, append to cssList"""
        for loc in self.locList:
            partitionList = [design.generatePt(loc, self.locList) for design in self.designList]
            #[print(pt) for pt in (flatten(partitionList))]
            self.cssList.append(Css(loc, flatten(partitionList)))

        print("LOOK HERE") 
        #print(self.cssList[1].diff(self.cssList[2]))

        return [css for css in self.cssList]

    def addDesign(self, element):
        self.designList.append(element)


"""Takes parameters and returns """
class DesignElement(object):

    """Conditions:
        1. Only Loc, specific partition (e.g. PT-CMS)
        2. Only LocList, partition for all locations (e.g. PT-Austin-Devices)
        3. Loc and Func, location specific function (e.g. PT-Austin-Conference)"""

    def toString(self): pass


class SpecificElement(DesignElement):
    
    def __init__(self, partition):
        self.partition = partition

    def generatePt(self, _, __):
        return [Partition(self.partition)]


class GenericElement(DesignElement):
    
    def __init__(self, function):
        self.func = function

    def generatePt(self, _, locList):
        return [Partition("PT-{}-{}".format(loc, self.func)) for loc in locList]


class LocSpecificElement(DesignElement):

    def __init__(self, function):
        self.func = function

    def generatePt(self, loc, _):
        return [Partition("PT-{}-{}".format(loc, self.func))]

