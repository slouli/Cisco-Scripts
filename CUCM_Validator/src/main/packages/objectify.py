class Location(object):

    def __init__(self, name):
        self.name = name.split("-")[1]
        self.cssList = None  #Eventually associate offices with associated CSSes


class LocationList(object):

    def __init__(self,locPoolList):
        self.locList = [Location(loc) for loc in locPoolList]


class Css(object):

    def __init__(self, name, ptList):
        self.name = name
        self.ptObjects = PartitionList(ptList)
        #print("\n===={}====\n".format(self.name))

    def __eq__(self, other):
        return self.name.__eq__(other.name) and self.ptObject.__eq__(other.ptObjects)

    def __str__(self):
        return str("\n===={}====\n{}".format(self.name, self.ptObjects))

    def __hash__(self):
        return self.name.__hash__()


    def diff(self, other):
        result = self.ptObjects.diff(other.ptObjects)

    def getPts(self):
        return self.ptObjects


class PartitionList(object):
    
    def __init__(self, ptList):
        #ptList must have elements of type Partition
        self.ptObjList = ptList

    @classmethod
    def fromStringList(cls, strList):
        #If pattern is in string format, use this constructor
        return cls([Partition(pt) for pt in strList])

    def diff(self, other):
        set1 = set(self.ptObjList)
        set2 = set(other.ptObjList)

        add = set1 - set2
        rmv = set2 - set1

        [print(pt) for pt in add]
        [print(pt) for pt in rmv]
        return "ADD: {}\nRMV: {}".format(add, rmv)

    def __str__(self):
        return "{}".format([str(pt) for pt in self.ptObjList])

    def toList(self):
        return [str(pt) for pt in self.ptObjList]


class Partition(object):
    
    def __init__(self, name):
        self.name = name
        self.loc = None
        self.func = None
        self.other = None
        self._parseName(name)


    def _parseName(self, name):
        nameList = name.split("-")
        if len(nameList) == 1: _ = tuple(nameList)
        if len(nameList) == 2: _, self.loc = tuple(nameList)
        if len(nameList) == 3: _, self.loc, self.func = tuple(nameList)
        if len(nameList) == 4: _, self.loc, self.func, self.other = tuple(nameList)
        return 

    def __eq__(self, ptObject):
        """
        if self.loc is not ptObject.loc: return False
        if self.func is not ptObject.func: return False
        if self.other is not ptObject.other: return False
        return True
        """
        return self.name.__eq__(ptObject.name)


    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        #return "<Partition Object: {}>".format(self.name)
        return self.name

offices = ['Addison','Alpharetta','Austin','Bellevue','Brentwood',
        'Burlington', 'Calgary', 'Chicago', 'Denver', 'Detroit',
        'Gaithersburg', 'Hilliard', 'Irvine', 'Lexington', 'Montreal',
        '']
