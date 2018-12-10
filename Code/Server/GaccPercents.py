# This Code is designed to lookup a GPS point
# and return metadata from the 
# Shapefile provided

import fiona
import pprint
from shapely.geometry import shape,Point, Polygon
import shapely.affinity
from descartes import PolygonPatch
import numpy as np
#MatPlot is only needed if you would like to use the plotter functions. 
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection

# Reads in the row and determines the index of each columns
# Returns a tuple giving the (Lat Index, Long Index,Year Index)
# Takes in the first line of the file
def find_headers(header):
    lat_index   = -1
    lng_index   = -1
    yr_index    = -1
    #find indexes for data
    for index in range(len(header)):
        if r"Lat Decimal" in header[index] :
            lat_index = index
        if r"Long Decimal" in header[index]:
            lng_index = index
        if r"Year" in header[index]:
            yr_index = index
    return (lat_index,lng_index,yr_index)


# Keys is the column header in the Shapefile to pull data from
# It can be passed as an optional argument if needed
# Function determines which zones intersect the circle
def poly_lookup (lookup,circle,keys=["NAT_CODE"]):
    found = []
    #List of values to be returned and the order they are returned in
    for i in lookup:
        if circle.intersects(i[0]):
            found.append(i)
            #plotter(i[0])
    return found



# Keys is the column header in the Shapefile to pull data from
# It can be passed as an optional argument if needed
# Function determines which zone the point is in
def point_lookup (lookup,point,keys=["NAT_CODE"]):
    found = []
    data  = []
    #List of values to be returned and the order they are returned in
    for i in lookup:
        if point.within(i[0]):
            found = i[1]
    for j in keys:
        data.append(found[j])
    return data

def create_list(file):
    data = []
    length = len(file)
    for i in range(length):
        current = file.next()
        shp_geom = shape(current['geometry'])
        meta = current['properties']
        data.append((shp_geom,meta))
    return data

# Takes two shapely geometry objects and plots them
# Put the larger one first
def plotTwo(one,two):
    cm = plt.get_cmap('RdBu')
    num_colours = 2
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = one.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    patches = []
    patches.append(PolygonPatch(two, ec='#555555', lw=0.2, alpha=1., zorder=1))
    patches.append(PolygonPatch(one, ec='#555555', lw=0.2, alpha=1., zorder=1))
    
    
    ax.add_collection(PatchCollection(patches, match_original=True))
    
    cmap = plt.get_cmap('RdYlBu')
    nfloors = np.random.rand(num_colours)
    colors = cmap(nfloors)

    collection = PatchCollection(patches)
    collection.set_color(colors)
    
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
    plt.show()


# Takes a shapely geometry object and plots it
def plotter(mp):
    cm = plt.get_cmap('RdBu')
    num_colours = 1
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = mp.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)

    patches = []
    patches.append(PolygonPatch(mp, ec='#555555', lw=0.2, alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
    plt.show()
# Takes a list of shapely geom objects and a circle.
# Plots the cirlce ontop of the list to visualize the overlap
def multi_Plotter(mp,circle):
    cm = plt.get_cmap('RdBu')
    num_colours = len(mp) + 1
    fig = plt.figure()
    ax = fig.add_subplot(111)
    minx, miny, maxx, maxy = circle.bounds
    w, h = maxx - minx, maxy - miny
    ax.set_xlim(minx - 0.2 * w, maxx + 0.2 * w)
    ax.set_ylim(miny - 0.2 * h, maxy + 0.2 * h)
    ax.set_aspect(1)
    patches = []
    
    for i in mp:
        patches.append(PolygonPatch(i[0], ec='#555555', lw=0.2, alpha=1., zorder=1))
    #patches.append(PolygonPatch(circle, ec='#555555', lw=0.2, alpha=1., zorder=1))
    ax.add_collection(PatchCollection(patches, match_original=True))
    
    cmap = plt.get_cmap('RdYlBu')
    nfloors = np.random.rand(num_colours)
    colors = cmap(nfloors)

    collection = PatchCollection(patches)
    collection.set_color(colors)
   
    ax.add_collection(collection)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.title("Shapefile polygons rendered using Shapely")
    plt.tight_layout()
    plt.show()

# Takes a list and converts it into a row for a CSV output
def listToRow(given):
    result = ""
    for i in given:
        cleaned = str(i).rstrip().replace(",",":")
        result += cleaned + ","
    #Cuts off the last Trailing comma and adds new line
    
    result = result.replace(",",":")
    return result[:-1] + "\n"


# Determines what % of the Gacc is in which region
# Returns a list of each regions and the %
def calcArea(Gacc,polygons):
    gaccArea = Gacc.area
    output = []
    for poly in polygons:
        overlap = Gacc.intersection(poly[0])
        overlapArea =overlap.area / gaccArea 
        output.append((poly[1]["NAT_CODE"],overlapArea))
    return output

# TODO
# Takes in a year or year index and determines which shapefile to 
# use for the given dataset
def setShapeFile(year,shapefileDict):
    if (year in shapefileDict.keys()):
        return shapefileDict[year]
    else:
        if (year == "2008"):
            return shapefileDict["2009"]

# Writes a list of outputs and header to a file
# prints when finished
def writeFile(outputList,header,filename):
    file = open(filename,'w+')
    headerStr = ""
    for i in header:
        headerStr += str(i) + ","
    headerStr = headerStr[:-1]

    file.write(headerStr)

    for i in outputList:
        file.write(i)
    
    file.close()
    print("Wrote to file: " , filename)

# Iterates through the given list of years and creates a lookup table for each year
# this lookup table is then stored in a dictionary where the key is the year
def createShapefileDict (years,mainPath):
    lookupDict = {}
    for i in years:
                                        #this String (r"path") is only needed if we must go deeper to find the folders of the shapfiles
        poly = fiona.open(mainPath + r"\IHT Project\PointLookup\PSA Data" + "\\" + i)
        lookup = create_list(poly)
        lookupDict[i] = lookup
    return lookupDict


if __name__ == '__main__':
    print("Check Point")
    # List of all available shapefiles to pull from (Should be the name of the folde the shapefile is in)
    years = ["2007","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018"]

    #Load in GACC data
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    gaccPath = mainPath + r"\IHT Project\PointLookup\PSA Data\GACC"
    csv_output    = mainPath + r"\IHT Project\PointLookup\output2.csv"

    shapefileDict = createShapefileDict(years,mainPath)
    poly = fiona.open(gaccPath)
    gacc = create_list(poly)
    header = ["Year","GACC","NAT_CODE_PERCENTAGE\n"]
    output = []
    for year in years:
        print(year)
        yearShape = setShapeFile(year,shapefileDict)
        for region in gacc:
            contained = poly_lookup(yearShape,region[0])
            codePercent = calcArea(region[0],contained)
            dataCleaned = listToRow(codePercent)
            output.append(str(year) + "," + str(region[1]['GACC_Label']) + "," + dataCleaned)
    writeFile(output,header,csv_output)
    