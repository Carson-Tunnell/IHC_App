import time
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt



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
    r = 3956 # Radius of earth in kilometers. Use 3956 for miles
    return c * r





if __name__ == '__main__':
    
    filename = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"
    #filename = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor"
    print("Starting...")
    print("Loading: " ,filename)

    start_time = time.process_time()

    graph = nx.read_shp(filename,simplify=True)
    graph = graph.to_undirected()
    end_time = time.process_time()
    print("Load in: {:.5f} secs".format(end_time - start_time))
    print(nx.info(graph))
    print(nx.number_of_nodes(graph))
    nodes = list(graph.nodes())
    #nodes = list(temp_nodes)

    #one = nx.get_edge_attributes(graph,'DIST_MILES')
    #print(one)

    start = 1000
    end   = 2000
    print(nodes[start])
    print(nodes[end])
    
    edges = list(graph.edges)

    #for (u, v, wt) in graph.edges.data('DIST_MILES'):
     #   print(u, v, wt)


    correct_graph = nx.Graph()
    #Calculates the shortest distances between the two points
    for k in graph.edges():
        dist = haversine(k[0][0],k[0][1],k[1][0],k[1][1])
        correct_graph.add_edge(k[0],k[1],length=dist)
        #print(k)
        #print(dist)

    for k in correct_graph.edges:
        print(k)

    route = nx.shortest_path(graph, source=nodes[start], target=nodes[end])
    #print(route)
    dist = nx.shortest_path_length(correct_graph, source=nodes[start], target=nodes[end],weight='length')
    #dist = nx.shortest_path_length(graph, source=nodes[start], target=nodes[end],weight='DIST_MILES')
    print(dist)

    #nx.draw_networkx(graph,with_labels=False,node_size=1)
    #plt.tight_layout()



    #calc distances between nodes and update them with the edge length