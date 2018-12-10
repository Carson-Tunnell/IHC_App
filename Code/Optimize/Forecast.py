# Code to download the forecasted fire data and determine which point gets what data and the GACC it is in
import urllib.request
import fiona
import pprint
from matplotlib import pyplot as plt
from shapely.geometry import shape,Point, Polygon
import zipfile
from matplotlib.collections import PatchCollection
from descartes import PolygonPatch


# https://gis.stackexchange.com/questions/113799/how-to-read-a-shapefile-in-python

def download_zip(url,filepath):

    urllib.request.urlretrieve(url, filepath + ".zip")
    unzip(filepath)

def unzip(filepath):    
    zip_ref = zipfile.ZipFile(filepath + ".zip", 'r')
    zip_ref.extractall(filepath + r"\psa_7_day")
    zip_ref.close()


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

def create_list(file):
    print()
    data = []
    length = len(file)
    print(length)
    for i in range(length):
        current = file.next()
        shp_geom = shape(current['geometry'])
        meta = current['properties']
        data.append((shp_geom,meta))
    return data

def point_lookup (lookup,point):
    found = []
    data  = []
    #List of values to be returned and the order they are returned in
    keys  = ["GACC_Label","D1","D2","D3","D4","D5","D6","D7"]
    for i in lookup:
        if point.within(i[0]):
            found = i[1]
            #plotter(i[0])
    for j in keys:
        data.append(found[j])
    #pprint.pprint(data)
    return data

def run():
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    url           = r"https://psgeodata.fs.fed.us/data/dynamic/psa_7_day.zip"
    shapfile_path = mainPath + r"\IHT Project\Data\Optimize Data\Forecast\psa_7_day"
    zip_path      = mainPath + r"\IHT Project\Data\Optimize Data\Forecast"
    csv_path      = mainPath + r"\IHT Project\Data\Server\Output.csv"

    download_zip(url,zip_path)
    poly = fiona.open(shapfile_path)
    lookup = create_list(poly)

    return lookup



if __name__ == '__main__':
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    
    url           = r"https://psgeodata.fs.fed.us/data/dynamic/psa_7_day.zip"
    shapfile_path = mainPath + r"\IHT Project\Data\Optimize Data\Forecast\psa_7_day"
    zip_path      = mainPath + r"\IHT Project\Data\Optimize Data\Forecast"
    csv_path      = mainPath + r"\IHT Project\Data\Server\Output.csv"
    #download_zip(url,zip_path)
    poly = fiona.open(shapfile_path)
    lookup = create_list(poly)



    #print (poly.schema)
   # first = poly.next()
    p1 = Point(-93.00, 40.00)
  
    point_lookup(lookup,p1)