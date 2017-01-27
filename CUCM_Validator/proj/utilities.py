import re
from packages.soap import SqlQuery
from lxml import etree

def partitionFilter(pts, pattern):
    return [partition for partition in pts if re.search(pattern, partition)]

def ptSub(pts, match, sub):
    p = re.compile(match)
    return {partition: p.sub(sub,partition) for partition in pts}

def getPartitions():
    getPts = "select pkid, name from routepartition"
    xmlPts = etree.fromstring(SqlQuery(getPts).execute())
    pts = xmlPts.xpath("//name/text()")
    return pts

