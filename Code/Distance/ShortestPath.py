# https://automating-gis-processes.github.io/2017/lessons/L7/network-analysis.html
# http://geoffboeing.com/2016/11/osmnx-python-street-networks/
# https://github.com/gboeing/osmnx/issues/153
# https://git.skewed.de/count0/graph-tool
# Load graph from JSON or XML file
# https://github.com/gboeing/osmnx/pull/95

#Convert NetworkX to GraphTools
#https://bbengfort.github.io/snippets/2016/06/23/graph-tool-from-networkx.html

import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import time
place_name = "Kamppi, Helsinki, Finland"
#place_name = "Fort Collins,Colorado, USA"
print("Loading Map...")
ox.utils.config(use_cache=True)
loading_start = time.process_time()
graph = ox.graph_from_place(place_name, network_type='drive')
loading_stop = time.process_time()
print("Load in: {:.5f} secs".format(loading_stop - loading_start))

#fig, ax = ox.plot_graph(graph)
#edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
#edges.columns
#edges['highway'].value_counts()
#print("Coordinate system:", edges.crs)
graph_proj = graph#ox.project_graph(graph)
#fig, ax = ox.plot_graph(graph_proj)
plt.tight_layout()
nodes_proj, edges_proj = ox.graph_to_gdfs(graph_proj, nodes=True, edges=True)
#print("Coordinate system:", edges_proj.crs)
#edges_proj.head()
#stats = ox.basic_stats(graph_proj)
#stats
#area = edges_proj.unary_union.convex_hull.area
#stats = ox.basic_stats(graph_proj, area=area)
#extended_stats = ox.extended_stats(graph_proj, ecc=True, bc=True, cc=True)
#for key, value in extended_stats.items():
#    stats[key] = value
#pd.Series(stats)
#edges_proj.bounds.head()

from shapely.geometry import box
bbox = box(*edges_proj.unary_union.bounds)
print(bbox)
orig_point = bbox.centroid
print("***********************************************************************************************")
print(orig_point)
nodes_proj['x'] = nodes_proj.x.astype(float)
maxx = nodes_proj['x'].max()
target_loc = nodes_proj.loc[nodes_proj['x']==maxx, :]
print(target_loc)
target_point = target_loc.geometry.values[0]
print(target_point)

orig_xy = (orig_point.y, orig_point.x)
target_xy = (target_point.y, target_point.x)
orig_node = ox.get_nearest_node(graph_proj, orig_xy, method='euclidean')
target_node = ox.get_nearest_node(graph_proj, target_xy, method='euclidean')
#o_closest = nodes_proj.loc[orig_node]
#t_closest = nodes_proj.loc[target_node]
print(orig_node)
print(target_node)
#od_nodes = gpd.GeoDataFrame([o_closest, t_closest], geometry='geometry', crs=nodes_proj.crs)

print("Finding Shortest Path")
short_start = time.process_time()
route = nx.shortest_path(G=graph_proj, source=orig_node, target=target_node, weight='length')
short_end = time.process_time()
print("Short in: {:.5f} secs".format(short_end - short_start))



print(route)
fig, ax = ox.plot_graph_route(graph_proj, route, origin_point=orig_xy, destination_point=target_xy)
plt.tight_layout()