import osmnx as ox
import networkx as nx
import time
from shapely.geometry import box
#https://www.latlong.net/degrees-minutes-seconds-to-decimal-degrees
if __name__ == "__main__":
 
    #filename = r"kamppi.osm"
    filename = r"delaware-latest.osm"
    #filename = r"C:\Users\ctunnell\Desktop\singapore.osm"

    
    start_time = time.process_time()
    
    #G = ox.core.graph_from_file(filename, network_type='drive', simplify=True)

    maxx = 24.9416784 
    maxy = 60.1711515

    minx = 24.9209141
    miny = 60.1609419
    
    #Fort Collins
    #maxx = -105.0763 
    #maxy = 40.58147
    #Greeley
    #minx = -104.9892
    #miny = 40.4233


                   #box(minx, miny, maxx, maxy, ccw=True):
     # bounding_box = box(minx + .05,miny + .05,maxx + .05,maxy + .05)
     # bounding_box = box(40.357103,-104.634249,40.611960,-105.154726)
     # G = ox.core.graph_from_polygon(bounding_box)

    G = ox.core.graph_from_bbox(north=maxy + 0.05,south=miny - 0.05,east=maxx + 0.05,west=minx - 0.05, network_type='drive', simplify=True)
    #G is a networkx Multigraph
    # Will be converted into Graph-Tools and run through that shortest path



    #Tuples need to be in decimal degrees from Lat Long
    start_tup = (60.1711515,24.9416784)
    end_tup   = (60.1609419,24.9209141)
    
    start = ox.get_nearest_node(G,start_tup,method='euclidean')
    end   = ox.get_nearest_node(G,end_tup  ,method='euclidean')

    short_start = time.process_time()
    route = nx.shortest_path(G=G, source=start, target=end, weight='length')
    short_end = time.process_time()
    print("Short in: {:.5f} secs".format(short_start - short_end))

    end_time = time.process_time()
    print("Ran in: {:.5f} secs".format(end_time - start_time))
    print("Done")
    #ox.plot_graph(ox.project_graph(G))
    fig,ax = ox.plot_graph_route(G, route, origin_point=start_tup, destination_point=end_tup)
    print(route)
    print("Displayed")