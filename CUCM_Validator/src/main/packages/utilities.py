import re
from packages.soap import SqlQuery
from lxml import etree

def flatten(listOfLists):
    return [val for sublist in listOfLists for val in sublist if val is not None]

def partitionFilter(pts, pattern):
    return [partition for partition in pts if re.search(pattern, partition)]

def ptSubstitute(pts, match, sub):
    p = re.compile(match)
    return {partition: p.sub(sub,partition) for partition in pts}

def cssFilter(cssDict, pattern):
    return {cssName:cssDict[cssName] for cssName in cssDict if re.search(pattern, cssName)}

def getPartitions():
    getPts = "select pkid, name from routepartition"
    xmlPts = etree.fromstring(SqlQuery(getPts).execute(True))
    pts = xmlPts.xpath("//name/text()")
    return pts

def getCallingSearchSpaces():
    getCss = "select name, clause from callingsearchspace"
    xmlCss = etree.fromstring(SqlQuery(getCss).execute(True))
    cssNames = xmlCss.xpath("//name/text()")
    cssPts = xmlCss.xpath("//clause/text()")
    css = {css_name: set(partitions.split(':')) for (css_name, partitions) in zip(cssNames, cssPts)}
    return css

def getLocations():
    getLocs = "select name from location where name like 'Loc-%'"
    xmlLocs = etree.fromstring(SqlQuery(getLocs).execute(True))
    _, allLocs = zip(*[loc.split("-") for loc in xmlLocs.xpath("//name/text()")])
    EXCLUSION_LIST = {"CMS", "ILS"}
    locs = sorted(list(set(allLocs) - EXCLUSION_LIST))
    return locs

def getDeviceName(xml):
    xmlPhones = etree.fromstring(xml)
    deviceNames = xmlPhones.xpath("//name/text()")
    deviceProfiles = xmlPhones.xpath("//currentProfileName/text() | //currentProfileName[not(text())]")
    
    deviceTupleList = list(zip(deviceNames, deviceProfiles))
    filteredList = [(device, profile) for (device, profile) in deviceTupleList if type(profile) is etree._ElementUnicodeResult]
    return filteredList

def getConfirmation():
    confirm = str(input("Are you sure you want to execute [n]: "))
    if confirm is "y" or confirm is "ye" or confirm is "yes": return True
    else: return False
