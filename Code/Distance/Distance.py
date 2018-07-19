#Distance program
#Designes to pull from other class files and execeute program
import time
import bisect
import networkx as nx
import osmnx as ox
import sys
from math import radians, cos, sin, asin, sqrt

#Boolean to control Debug output through Program
debug = False
timing_debug = False
all_nodes         = []
long_sorted_nodes = []
lat_sorted_nodes  = []
long_key          = []
lat_key           = []
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
        all_nodes.append((k[0][0],k[0][1]))
        all_nodes.append((k[1][0],k[1][1]))
        #correct_graph.add_node((k[0][0],k[0][1]),x=k[0][0],y=k[0][1])
        #correct_graph.add_node((k[1][0],k[1][1]),x=k[0][0],y=k[0][1])        
        correct_graph.add_edge(k[0],k[1],length=dist)
    
    calc_start = time.process_time()
    
    
  
    #keys = [r[1] for r in data] 
    calc_end = time.process_time()
    if (timing_debug): print("Sort in: {:.5f} secs".format(calc_end - calc_start))

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
def closest_node(start,graph,first = 5.00,second = 100.00):   
    calc_start = time.process_time()                   #TODO Optimize searching for closest point, No Nodes found Error
    for k in graph.nodes():
        #Check K indexed, Finds closest node in the graph within first miles of given point
        if haversine(start[0],start[1],k[1],k[0]) <= first:
            calc_end = time.process_time()
            if (timing_debug): print("Closest 1st in: {:.5f} secs".format(calc_end - calc_start))
            return k
    #If node is not found in first miles expand and look again for second miles
    #50 chosen based on Shapfile provided since that would account for the most isolated point possible
    for k in graph.nodes():
        #Check K indexed, Finds closest node in the graph within 50 miles of given point
        if haversine(start[0],start[1],k[1],k[0]) <= second:
            calc_end = time.process_time()
            if (timing_debug): print("Closest 2nd in: {:.5f} secs".format(calc_end - calc_start))
            return k
    print("NO NODES FOUND: RETURNED NONE")
    
    calc_end = time.process_time()
    if (timing_debug): print("Closest in: {:.5f} secs".format(calc_end - calc_start))

def find_long(start):
    i = [bisect.bisect_left(long_key, start[1] + 1)][0]
    j = [bisect.bisect_left(long_key, start[1] - 1)][0]

    long_search = long_sorted_nodes[j:i]
    #print("Long Len: ", len(long_search))
    return(long_search)

def find_lat(start):
    i = [bisect.bisect_left(lat_key, start[0] + 0.25)][0]
    j = [bisect.bisect_left(lat_key, start[0] - 0.25)][0]

    lat_search = lat_sorted_nodes[j:i]
    return(lat_search)

def intersect(a, b):
    """ return the intersection of two lists """
    return list(set(a) & set(b))

def generate_globals(graph):
    global lat_key
    global long_key
    for k in graph.nodes():
        all_nodes.append(k)
    all_nodes.sort(key=lambda x: x[0])
    
    for k in all_nodes:
        long_sorted_nodes.append(k)
    
    all_nodes.sort(key=lambda x: x[1])
    for k in all_nodes:
        lat_sorted_nodes.append(k)

    lat_key  = [r[1] for r in lat_sorted_nodes ]
    long_key = [r[0] for r in long_sorted_nodes]


def closest_node_optimized(start,graph):

    calc_start = time.process_time()

    long_found = find_long(start)
    lat_found = find_lat(start)

    valid_points = intersect(lat_found,long_found)
    #print("Valid Len: ", len(valid_points))
    nearest = find_nearest(start,valid_points)

    calc_end = time.process_time()
    if (timing_debug): print("Close in: {:.5f} secs".format(calc_end - calc_start))
    #print("Nearest: " ,nearest)
    return nearest

def find_nearest(start,valid_nodes):
    smallest = sys.maxsize
    node = None
    for k in valid_nodes:
       temp = haversine(start[0],start[1],k[1],k[0])
       if (temp < smallest):
           smallest = temp
           node = k
    return node


        

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
        calc_start = time.process_time() 
        dist = nx.shortest_path_length(graph, source=start_node, target=end_node,weight='length')
        calc_end = time.process_time()
        if (timing_debug): print("Shortest in: {:.5f} secs".format(calc_end - calc_start))
    except nx.exception.NetworkXNoPath:
         if debug: print("No Distance")
         return -1.0 
    else:
        return dist



def shortest_path_osmnx(start_point,end_point,graph):
    start_node  = closest_node_optimized(start_point,graph)
    end_node    = closest_node_optimized(end_point,graph)
    if debug:
        print("Nodes to use: ")
        print(start_node)
        print(end_node)
    if(start_node == None or end_node == None):
        return -2.0
    try:
        dist = nx.shortest_path_length(graph, source=start_node, target=end_node,weight='length')
    except nx.exception.NetworkXNoPath:
         if debug: print("No Distance")
         return -1.0 
    else:
        return dist




#Look at adding metadata for speed limit
#approximate 45mph for all roads
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



