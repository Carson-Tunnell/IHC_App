import Distance
import Input
import fileinput
import time
import sys
import os
import networkx as nx
import multiprocessing
from datetime import datetime


#Method to help start the Processes
#Takes a subset of the input file as row
#takes the column so it knows where to look as columns
#takes a shared memory array to store values with main process as results
#Takes a start index to store in results as start_index
#takes an end index to store in results as end_index
#takes a copy of the graph for finding paths as graph
def calc_distance(row,columns,results,start_index,end_index,graph):
    x = 0 
    Distance.generate_globals(graph)
    while (start_index < end_index):
        if((start_index % 100) == 0):
            print("Completed: ",start_index, "/" ,end_index)

        line,start,dest = Input.read_line_given(columns,row[x].split(','))
        #dist = Distance.shortest_path(start,dest,graph)
        dist = Distance.shortest_path_osmnx(start,dest,graph)
        if(type(dist) is float ):
            results[start_index] = dist
        start_index = start_index + 1
        x = x + 1
    print("Completed: ",start_index, "/" ,end_index)

def output_correct(output_path,count):
    halfs = output_path.split(".")
    halfs[0] = halfs[0] + str(count) + "."

    return halfs[0] + halfs[1]


    
if __name__ == '__main__':
    print("running main...")
    print(str(datetime.now()))
    
    #DATA that needs to be set for code to run#
    num_process = 8
    rows_of_data = 2500    #Includes header row
    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"
    CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Process"
    output_path    = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Folder_Demo.csv"

    if len(sys.argv) > 1 and len(sys.argv) < 6:
        #Rows and Process
        rows_of_data = float(sys.argv[1])
        num_process  = float(sys.argv[2])
    #All Arguments given
    if len(sys.argv) == 6:
        shapefile_path = sys.argv[1]
        CSV_path       = sys.argv[2]
        output_path    = sys.argv[3]
        rows_of_data   = float(sys.argv[4])
        num_process    = float(sys.argv[5]) 
    
    graph = Distance.correct_graph(Distance.load_shp(shapefile_path,True))
    slash = r"/"
    counter = 0
    #Looks at all .CSV files in a given directory
    for filename in os.listdir(CSV_path):
        if filename.endswith(".csv"):
            filepath = CSV_path + slash + filename
            print(filepath)
            print(filename)
            file = Input.open_file(filepath)
            columns,headers = Input.find_columns(file)

            todo = []
    
            for k in file:
                todo.append(k)
            file.close()
            todo_range = []
            

            rows_per = int(rows_of_data / num_process)

            for i in range(num_process):
                todo_range.append(rows_per * i)
            todo_range.append(rows_of_data)

            print(todo_range)

            results = multiprocessing.Array('d',rows_of_data - 1)
            processes = []
            for k in range(num_process):
                processes.append(multiprocessing.Process(target=calc_distance,args=(todo[todo_range[k]:todo_range[k+1]],columns,results,todo_range[k],todo_range[k+1] - 1,graph)))
                processes[k].start()

            #Deletes Graph to save memory
            graph = nx.Graph()
            
            for j in processes:
                j.join()    
            
            output_path_edit = output_correct(output_path,counter)

            with open(output_path_edit, "a") as output:
                output.write(",".join(map(str, headers)))
                for k in range(len(todo)):
                    todo[k] = todo[k].split(',')
                    todo[k][columns[4]] = results[k]
                    line_write =  ",".join(map(str, todo[k]))
                    output.write(line_write)
                    
            print("Wrote to file: ", output_path_edit)
            print(str(datetime.now()))
            counter += 1
