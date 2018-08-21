import osmnx as ox
import networkx as nx
import time
from shapely.geometry import box

import Distance
import Input
import fileinput


#https://www.latlong.net/degrees-minutes-seconds-to-decimal-degrees
if __name__ == "__main__":
 
    
    start_time = time.process_time()
    
    #shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"
    #gml_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways_gml" 
    #CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\LocationsThatNeedDistances.csv"

    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor"
    gml_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor_gml" 

    short_start = time.process_time()
    print("reading shape...")
    graph = Distance.correct_graph(Distance.load_shp(shapefile_path))
    short_end = time.process_time() 

    print(nx.info(graph))

#    print("writing GML..")
    #nx.write_graphml(graph,gml_path)

    print("Reading GML..")
    #gml_start = time.process_time()
    #new_graph = nx.read_graphml(gml_path)#, node_type=<type 'float'>)
    
    #gml_stop = time.process_time()
    #print(nx.info(new_graph))
    
    print("Load shp in: {:.5f} secs".format(short_end - short_start))
    #print("Load gml in: {:.5f} secs".format(gml_stop - gml_start))