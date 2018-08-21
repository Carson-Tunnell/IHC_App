#Distance program
#Designes to pull from other class files and execeute program

import Distance
import Input
import fileinput
import time
import _thread
import concurrent.futures

import multiprocessing
from threading import Thread
import subprocess


def process(row,columns,graph):
    line,start,dest = Input.read_line_given(columns,row.split(','))
    dist = Distance.shortest_path(start,dest,graph)
    line[columns[4]] = dist
    line_write =  ",".join(map(str, line))
    return line_write


def process_thread_shared(index,todo,columns,results,graph):
    #print("Running thread process...", index)
    x = index[0]
    i = 0
    print("Here", index)
    for x in range(index[1]):
        line = process(todo[x],columns,graph)
        print(line)
        #results[i] = float(line[len(line) - 1])
        print(results[i])
        i = i + 1
    return results

def process_thread(index,todo,columns,results,graph):
    #print("Running thread process...", index)
    x = index[0]
    print("Here", index)
    for x in range(index[1]):
        #print(x)
        results.append(process(todo[x],columns,graph))
    return results



if __name__ == '__main__':
    print("Starting Driver...")
    Input.set_debug(False)
    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"  
    #shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor"
    CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\LocationsThatNeedDistances.csv"
    #CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Problems.csv"
    #Loads the shapefile and gets the graph
    #Also runs correct graph on returned graph in one line instead of two
    graph = Distance.correct_graph(Distance.load_shp(shapefile_path,True))
    print("Map and Graph Loaded...")
    #Open CSV for reading and find column locations
    file = Input.open_file(CSV_path)
    columns,headers = Input.find_columns(file)
    print("CSV Loaded...")
    
    calc_start = time.process_time()
    results = []
    results.append(headers)
   

    todo = []
    for k in file:
        todo.append(k)
  

    first = (0,624)
    second = (625,1244)
    third = (1245,1869)
    fourth = (1869,2499)


    #manager = multiprocessing.Manager()
    p1_res = multiprocessing.Array('d',first[1] * 5)
    p1 = multiprocessing.Process(target=process_thread_shared, args=(first, todo,columns,p1_res ,graph))
    p1.start()
    p1.join()
    #manager  = multiprocessing.Manager()
    print(p1_res[:])
    #print(first_res)
    #print(second_res)
    #print(third_res)
    #print(fourth_res)


    #p = multiprocessing.Pool(process=4)
    #data = p.starmap(process_thread, (todo,columns,first_res ,graph))


    #p.map(process_thread, data)
    #(index,todo,columns,results):


    calc_end = time.process_time()
    print("Shortest in: {:.5f} secs".format(calc_end - calc_start))
   # for q in results:
    #    print(q) 
            

#https://docs.python.org/3/library/concurrent.futures.html


        


    