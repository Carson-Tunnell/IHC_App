from graph_tool.all import *



if __name__ == "__main__":
    print("Running...")
    filename = r""
    graph = graph_tool.load(filename,fmt="graphml")
    edges = graph.get_edges()

    for j in edges:
        print(j)