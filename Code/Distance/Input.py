#Program designed to read in data
#Can read in from a CSV or a database
import csv
import sys
import time

debug = False

def set_debug(boolean):
    debug = boolean

#Opens file and returns file object
#little redundant but allows future tweaks for folders if needed
def open_file(filename):
    file = open(filename) 
    return file

#find position of column headers and removes the headers from the CSV
#matches based on string comparisons
#Returns the index of the start and destination columns and the column to write data to
#Returned list indexes 
# [0]: start_lat
# [1]: start_long
# [2]: dest_lat
# [3]: dest_long
# [4]: dist column for output
def find_columns(file):
    start_lat = -1.0
    start_long = -1.0
    dest_lat = -1.0
    dest_long = -1.0
    dist = -1.0

    #Splits the header columns by a comma
    #returns a list that we can iterate through
    header = file.readline().split(',')
    #iterate through header based on index and not string
    #also finds DistanceInMi column for storing the values later
    for index in range(len(header)):
        if header[index] == "StartingPtLat":
            start_lat = index
        if header[index] == "StartingPtLong":
            start_long = index
        if header[index] == "DestinationLat":
            dest_lat = index
        if header[index] == "DestinationLong":
            dest_long = index
        if header[index] == "DistanceInMi":
            dist = index
    if debug:
        print("StartingPtLat: "  ,start_lat)
        print("StartingPtLong: " ,start_long)
        print("DestinationLat: " ,dest_lat)
        print("DestinationLong: ",dest_long)
        print("DistanceInMi: "   ,dist)

    #Returns a list of all the needed points
    #the list makes it easier to pass between functions and cleans the code a litte
    #optinal return of list of headers in the file
    return [start_lat,start_long,dest_lat,dest_long,dist],header

#Reads in data given the locations of the columns with needed data
#takes in the file object to iterate over
#returns the whole line as a list [String] and the Tuple of Start (lat,long) dest (lat,Long)
#Tuple has been converted from String to Float for processing later
def read_line(columns,file):
    line = file.readline().split(',')
    start_tuple = (float(line[columns[0]]),float(line[columns[1]]))
    dest_tuple  = (float(line[columns[2]]),float(line[columns[3]]))
    return line,start_tuple,dest_tuple

#Performs same function as read_lines but instead of accessing file user provides the line 
def read_line_given(columns,line):
    start_tuple = (float(line[columns[0]]),float(line[columns[1]]))
    dest_tuple  = (float(line[columns[2]]),float(line[columns[3]]))
    return line,start_tuple,dest_tuple


if __name__ == '__main__':
    if debug:
        print("Starting Input Program...")
        start_time = time.process_time()
    
    #Takes argument for CSV filepath
    #filename = sys.argv[1]
    filename = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\LocationsThatNeedDistances.csv"

    file = open_file(filename)
    columns = find_columns(file)

    line,start,dest = read_line(columns,file) 
    print(start)
    print(dest)

    line,start,dest = read_line(columns,file)
    print(start)
    print(dest)

    file.close()
    
    if debug:
        end_time = time.process_time()
        print("Load in: {:.5f} secs".format(end_time - start_time))