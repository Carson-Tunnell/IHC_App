#Driver program
#Designes to pull from other class files and execeute program
import time
import osmnx as ox
import matplotlib.pyplot as plt

#Boolean to control Debug output through Program
debug = True

#takes a filepath to a shapefile
#filepath should be a directory(folder) with all the files that make up the shape file
#Loads the shapefile into Networkx and creates nodes and edges
#All attributes from the shapefile will be preserved but distances should not be used
#Returns the graph object
def load_shp(filename):
    #simplify can speed the loading up but has slight reduction in precision.
    if debug:
        print("Loading file: ", filename)
        start_time = time.process_time()
    graph = nx.read_shp(filename,simplify=True) 

    if debug:
        end_time = time.process_time()
        print("Load in: {:.5f} secs".format(end_time - start_time))
    return graph.to_undirected()

#Networkx preserves the distance but splits up edges and duplicates the attributes
#This produces distances when finding paths that are too large and innacurate
#Correct_Graph takes all points and adds an attribute called length
#Uses the Haversine formula to calculate distance between nodes and adds the edges into a graph
#Adding edges automatically adds the correct nodes to the graph as well
#returns a new graph of points with attribute called length with correct distance between points
def correct_graph(graph):
    for k in graph.edges():
        #each edge is a nested tuple      ((long1,lat1)  (long2,lat2))
        #                                  [0][0] [0][1] [1][0] [1][1]
        dist = haversine(k[0][0],k[0][1],k[1][0],k[1][1])
        correct_graph.add_edge(k[0],k[1],length=dist)
    return correct_graph


#Haversine formula to calculate distance between points
#Returns value in miles and takes into account Earth curvature
#https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in Miles. Use 6371 for Kilometers
    return c * r


#Takes a tuple (lat,long) and finds the closest node already in the graph.
#Uses the (lat,long) to loop through the graph and find nodes
#if a node has a distance of less than 10 miles it will be returned
def closest_node(start,graph):
    for k in graph.nodes():
        #Check K indexed
        if haversine(start[1],start[0],k[1],k[0]) <= 10.00:
            return k

#return list of Routes to be calcualted
def read_csv(filename):
    print(filename)
    

#Main function to control flow of program and call functions
#Filename is hard coded but can be set via program arguments
if __name__ == '__main__':
    print("Starting Program...")
    #set filepath for shapefile directory
    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"  
    csv_path = r"csv location"  
    #saves graph 
    graph = load_shp(shapefile_path)
    #overwrites graph with corrected version
    graph = correct_graph(graph)

    #Read in CSV and determine which points need to be calcualted
    route_list = read_csv(csv_path)
    #Find nearest Node in graph to calculate distances from

    #Take distance and estimate drive time (Shortest Path)

    #



