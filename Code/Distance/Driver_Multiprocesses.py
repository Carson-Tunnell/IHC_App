import sys
sys.path.insert(0, r'C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Code\Optimize')
import Distance
import Input
import Reader
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

#Copy of the main function so it can be run from other classes
def start(shapefile_path="",CSV_path="",output_path="",num_process_given=4):
    num_process = num_process_given

    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"

    shapefile_path = mainPath + r"\IHT Project\Maps\Test\Middle2"
    CSV_path       = mainPath + r"\IHT Project\Data\Optimize Data\Output"
    output_path    = mainPath + r"\IHT Project\Data\Optimize Data\Folder_Demo.csv"

    # Generates the graph to be used for distances
    graph = Distance.correct_graph(Distance.load_shp(shapefile_path,False))
    slash = r"/"
    counter = 0
    #Looks at all .CSV files in a given directory
    for filename in os.listdir(CSV_path):
        if filename.endswith(".csv"):
            filepath = CSV_path + slash + filename
            print(filepath)
            print(filename)
            file = Input.open_file(filepath)

            rows_of_data = sum(1 for line in open(filepath))
            print(rows_of_data)
            columns,headers = Input.find_columns(file)
            # Todo is a list of distances that need to be processes
            # it is used to break up into parallel processes
            todo = []
    
            for k in file:
                todo.append(k)
            file.close()
            todo_range = []
            # Determines how many rows each process will get
            rows_per = int(rows_of_data / num_process)

            for i in range(num_process):
                todo_range.append(rows_per * i)
            todo_range.append(rows_of_data)

            print(todo_range)
            # Genereates the shared memory list in RAM
            results = multiprocessing.Array('d',rows_of_data - 1)
            processes = []
            # Spawns processes that will calculate the distances
            for k in range(num_process):
                processes.append(multiprocessing.Process(target=calc_distance,args=(todo[todo_range[k]:todo_range[k+1]],columns,results,todo_range[k],todo_range[k+1] - 1,graph)))
                processes[k].start()

            #Deletes Graph to save memory
            graph = nx.Graph()
            # Waits for all the processes to complete before moving on
            for j in processes:
                j.join()    
            
            output_path_edit = output_correct(output_path,counter)
            # Writes the output to file
            with open(output_path_edit, "a") as output:
                output.write(",".join(map(str, headers)))
                for k in range(len(todo)):
                    todo[k] = todo[k].split(',')
                    todo[k][columns[4]] = results[k]
                    line_write =  ",".join(map(str, todo[k]))
                    output.write(line_write)
                    
            print("Wrote to file: ", output_path_edit)
            print(str(datetime.now()))
            addToDatabase(output_path_edit)
            counter += 1

# Adds the output distance values to the database to be used for look up
# later on in the website
def addToDatabase(filename):
    conn = Reader.connect("root","Code","localhost","iht_test")
    cursor = conn.cursor()
    file = open(filename)
    header = file.readline()
    header = header.split()
    resID,destIncID,distanceInMi,forecast = find_columns(header)
    for line in file.readlines():
        splat = line.split(',')
        addDistance(cursor,splat[resID],splat[destIncID],splat[distanceInMi],splat[forecast],header)
    conn.commit()  

def addDistance(cursor,resID,destIncID,distanceInMi,forecast,header):
    if(not checkDuplicate(cursor,resID,destIncID,distanceInMi,forecast)):
        addUnique(cursor,resID,destIncID,distanceInMi,forecast)
    updateDist(cursor,resID,destIncID,distanceInMi,forecast,header)
        

def addUnique(cursor,resID,destIncID,distanceInMi,forecast):
    query = "INSERT INTO distancelookup Values (" + str(int(resID)) + ", " + str(int(destIncID))+ \
            ", " + str(distanceInMi) + ", " + str(forecast) + ");"
    cursor.execute(query)
    

def updateDist(cursor,resID,destIncID,distanceInMi,forecast,header):
    query = "UPDATE distancelookup SET "
    query +=  "`ResID` = '" + resID +  "', `DestIncID` = '" + destIncID + \
              "', `DistanceInMi` = '" + distanceInMi + "', `Forecast` = '" + forecast +"';"  
    cursor.execute(query)
    
    #Insert into DB


# Checks for duplicates
# True if duplicate
# False if unique
# only checks for res ID and dest ID since distance and forecast can change
def checkDuplicate(cursor,resID,destIncID,distanceInMi,forecast):
    query = "SELECT * From distancelookup WHERE `ResID` like '" + str(resID) + "' and `DestIncID` like '" \
            + str(destIncID) + "';"
    cursor.execute(query) 
    
    result = cursor.fetchone()
    if (result != None):
        return True
    else:
        return False

def find_columns(header):
    resID = -1
    destIncID= -1
    distanceInMi = -1
    forecast = -1
    
    for index in range(len(header)):
        if  "ResID" in header[index] :
            resID = index
        if "DestIncID" in header[index]:
            destIncID = index
        if "DistanceInMi" in header[index]:
            distanceInMi = index
        if "Forecast" in header[index] :
            forecast = index
    return (resID,destIncID,distanceInMi,forecast)
    
if __name__ == '__main__':
    start()