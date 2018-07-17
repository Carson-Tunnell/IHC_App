#Distance program
#Designes to pull from other class files and execeute program
import time
import networkx as nx
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt

#Boolean to control Debug output through Program
debug = False

#takes a filepath to a shapefile
#filepath should be a directory(folder) with all the files that make up the shape file
#Loads the shapefile into Networkx and creates nodes and edges
#All attributes from the shapefile will be preserved but distances should not be used
#has optional argument boolean on simplifying the graph object to be returned
#Returns the graph object
def load_shp(filename,simple=True):
    #simplify can speed the loading up but has slight reduction in precision.
    if debug:
        print("Loading file: ", filename)
        start_time = time.process_time()

    graph = nx.read_shp(filename,simplify=simple) 
    
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
def correct_graph(graph):  ##Optimize for searches and finding nearest nodes
    correct_graph = nx.Graph()
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
    return abs(c * r)


#Takes a tuple (lat,long) and finds the closest node already in the graph.
#Uses the (lat,long) to loop through the graph and find nodes
#if a node has a distance of less than first miles it will be returned
#Else it will look again for a node within second miles and return that
#Second should be a worst case situation for an isolated point based on the provided shapefile
#Fist and Second are distances to look for a point in the graph
def closest_node(start,graph,nodes_sorted = None,first = 5.00,second = 100.00):                      #TODO Optimize searching for closest point, No Nodes found Error
    for k in graph.nodes():
        #Check K indexed, Finds closest node in the graph within first miles of given point
        if haversine(start[0],start[1],k[1],k[0]) <= first:
            return k
    #If node is not found in first miles expand and look again for second miles
    #50 chosen based on Shapfile provided since that would account for the most isolated point possible
    for k in graph.nodes():
        #Check K indexed, Finds closest node in the graph within 50 miles of given point
        if haversine(start[0],start[1],k[1],k[0]) <= second:
            return k
    print("NO NODES FOUND: RETURNED NONE")

def closest_node_optimized(start,graph,nodes_sorted = None,first = 5.00,second = 100.00):
    print("optimal")


#Takes a start and end tuple of lat,long and finds the shortest distance
# looks up closests nodes based on tuple cooridantes
# calcualtes distance between closest found nodes in the grap
# returns distance in miles based on the two found nodes            
def shortest_path(start_point,end_point,graph):
    start_node  = closest_node(start_point,graph)
    end_node    = closest_node(end_point,graph)
    if debug:
        print("Nodes to use: ")
        print(start_node)
        print(end_node)
    try:
        dist = nx.shortest_path_length(graph, source=start_node, target=end_node,weight='length')
    except nx.exception.NetworkXNoPath:
         if debug: print("No Distance")
         return -1.0 
    else:
        return dist



def shortest_path_Astar(start_point,end_point,graph):
    start_node  = closest_node(start_point,graph)
    end_node    = closest_node(end_point,graph)
    if debug:
        print("Nodes to use: ")
        print(start_node)
        print(end_node)
    try:
        dist = nx.astar_path_length(graph, source=start_node, target=end_node,heuristic=heuristic_helper,weight='length')
    except nx.exception.NetworkXNoPath:
         if debug: print("No Distance")
         return -1.0 
    else:
        return dist


def heuristic_helper(start,end):
    return float(haversine(start[0],start[1],end[1],end[0]))


#return list of Routes to be calcualted
def read_csv(filename):
    print(filename)

#Look at adding metadata for speed limit
#approximate 40mph for all roads
def travel_time():
    print("Time")
    

#Main function to control flow of program and call functions
#Filename is hard coded but can be set via program arguments
if __name__ == '__main__':
    print("Starting Program...")
    #set filepath for shapefile directory
    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"  
    #shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor"
    csv_path = r"csv location"  
    #saves graph 
    graph = load_shp(shapefile_path)
    #overwrites graph with corrected version
    graph = correct_graph(graph)    

    #Read in CSV and determine which points need to be calcualted
    route_list = read_csv(csv_path)
    #Find nearest Node in graph to calculate distances from
    start_point = (40.366061,-105.561123) 
    end_point   = (40.5603  ,-105.082544)
    end_point2  = (37.362637,-118.410867)
    #Take distance and estimate drive time (Shortest Path)
    short_start = time.process_time()
    
    #dist = shortest_path(start_point,end_point,graph)
    dist = shortest_path_Astar(start_point,end_point,graph)
    print(dist)
    short_end = time.process_time()
    print("Shortest in: {:.5f} secs".format(short_end - short_start))

    short_start = time.process_time()
    dist = shortest_path_Astar(start_point,end_point2,graph)

    short_end = time.process_time()
    #print("Shortest2 in: {:.5f} secs".format(short_end - short_start))

    print(dist)
    #



