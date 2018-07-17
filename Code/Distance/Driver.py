#Distance program
#Designes to pull from other class files and execeute program

import Distance
import Input
import fileinput
import time

if __name__ == '__main__':
    print("Starting Driver...")
    Input.set_debug(False)
    shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Highways"  
    #shapefile_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Maps\Test\Minor"
    CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\LocationsThatNeedDistances.csv"
    #CSV_path       = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Problems.csv"
    #Loads the shapefile and gets the graph
    #Also runs correct graph on returned graph in one line instead of two
    graph = Distance.correct_graph(Distance.load_shp(shapefile_path))
    print("Map and Graph Loaded...")
    #Open CSV for reading and find column locations
    file = Input.open_file(CSV_path)
    columns,headers = Input.find_columns(file)
    print("CSV Loaded...")
    calc_start = time.process_time()

    with open(r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Problems_test_Small.csv", "a") as output:
        output.write(",".join(map(str, headers)))
        for k in file:
            line,start,dest = Input.read_line_given(columns,k.split(','))
            dist = Distance.shortest_path(start,dest,graph)
            #print(start)
            #print(dest)
            #print("Found: " ,start, dest, dist)
            #print("\n")
            line[columns[4]] = dist
            line_write =  ",".join(map(str, line))
            output.write(line_write)
    calc_end = time.process_time()
    print("Shortest in: {:.5f} secs".format(calc_end - calc_start))
            

        


    