# Program Driver for optimization
# main method takes files and computes the optimal solution
import numpy as np
import cvxopt
from cvxopt import printing
import cvxopt_helpers as op
import Reader
import pprint

# creates a circular array with wraparound
# used to read in data from the distance file in a manner that allows
# the C matrix to be created quickly later on
# Stores each crew and all their distances next to one another
# Eg: all of crew 1330 distances will be in indexes 0 - 30 if 30 requests are present
# uses simple % to loop back around to index 0 when index is > len
# changes the input array by reference, no return value
# **This is where we can add extra criteria like workload and weather**
def create_circular_array(filename,circle_array,num_crews,num_incident):
    file = open(filename)
    header = file.readline()
    counter = 0
    dist_index = find_dist_index(header)
    for line in file.readlines():
        line = line.split(',')
        circle_array[counter % num_crews][int(counter / num_crews)] = line[dist_index] # +  .5 * line[work_index] + .25 * line[F_index] .....
        counter += 1
    file.close()

# find the header column that contains the distance
# string matches the name of the distance column from a given file
# returns the index or -1 if not found
def find_dist_index(header):
    header = header.split(',')
    dist = -1
    #find indexes for data
    for index in range(len(header)):
        if r"DistanceInMi" in header[index] :
            dist = index
    if dist == -1:
        print("Error: DistanceInMi Column not Found...")

    return dist

# find the header column that contains the crews to send results
# columns should be empty or it will be overwrritten
# this is where the program will output the results from the optimization
# String mathces with crewsToSend and will return the given index from that
# returns the index with the column or -1 if not found
def parse_header(header):
    crew_index = -1
    for index in range(len(header)):
        if r"CrewsToSend" in header[index] or r"CrewToSend" in header[index] :
            crew_index = index
    if crew_index == -1:
        print("Error: CrewsToSend Column not Found...")

    return crew_index


# Solution array that is returned from the optimization is not formatted correcrtly
# this function changes the ordering of the results so they match the correct entry
# in the input file.  Changes solution array by reference but also returns the array
def format_solution(sol,num_crews,num_incident):
    #print(sol)
    new_array = cvxopt.matrix (np.zeros((num_crews * num_incident, 1)))
    index = 0
    for i in range(num_incident):
        j = i
        while j < sol.size[0]:
            new_array[index] = sol[j,0]
            j += num_incident
            index += 1
    sol = new_array
    return new_array

# Writes the solution into a new file.  New file is essentially a duplicate of the input file
# This function simply adds the output into the CrewsToSend column in the given CSV
# Prints when writting is completed
def write_answer(solution,filename,input_file,num_crews,num_incident):
    file_input = open(input_file)
    header = file_input.readline().split(',')
    crew_index = parse_header(header)

    output = open(filename,"w+")
    output.write(",".join(map(str, header)))
    sol_format = format_solution(sol['x'],num_crews,num_incident)
    for j in sol_format:
        line = file_input.readline().split(',')
        line[crew_index] = str(int(j))
        line_write =  ",".join(map(str, line))
        line_write += "\n"
        output.write(line_write)
    print("Wrote to: " ,filename)

# Used for debbuging
# prints each of the three generated Matricies as well as the solution matrix
# outputs into a CSV that can be opened in Excel for analysis
def write_all(a,b,c,sol,num_crews,num_incident,filename):
    file = open(filename,"w+")
    file.write("A \n")
    for i in range(a.size[0]):
        file.write("\n")
        for j in range(a.size[1]):
            file.write( str(a[(i,j)]) + ",")

    file.write("\n B \n")

    for i in b:
        file.write(str(i) + "\n")

    file.write("\n C \n")

    for i in c:
        file.write(str(i) + "\n")

    file.write("\n Sol \n")

    for i in sol['x']:
        file.write(str(i) + "\n")

    print("Wrote to: " ,filename)

if __name__ == '__main__':

    # Input files for the program
    # Pending: CSV containing the Requestst that need to be filled.  Program finds all that are listed as available
    # Homebase: Reference file that containts the Lat,Long of the homebases that is used to find distances
    # Crews: List of crew statuses
    # Requests: list of requests that contain distances, output from the Distance program
    # Output: Output file location for the optimization answers
    
    # Set requests (Output of distance code) as the input CSV and output to the output location
    requests = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Folder_Demo0.csv"
    output  = r"~\IHT Project\Data\Optimize Data\opt_out.csv"
    
    # add number of crews and incidents here
    # *************************************
    num_crews = 145
    num_incident = 79
    #pending  = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Reduced_Pending.csv"
    #homebase = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\HomeBase.csv"
    #crews    = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Reduced_Crews.csv"
    
    
    
   
    #conn = Reader.connect("root","Code","localhost","iht_test")
    #cursor = conn.cursor()

    # Reads in and stores the needed information into lists
    #pending_lines = Reader.get_pending(cursor)
    #homebase_lines = Reader.get_homebase(cursor)
    #crews_lines = Reader.get_crews(cursor)

    # Reads in the data from CSV's and not a database
    #pending_lines  = Reader.read_pending(pending)
    #homebase_lines = Reader.read_homebase(homebase)
    #crews_lines    = Reader.read_crews(crews)
    
    #print("Pending Requests: " , len(pending_lines))
    #print("Crews: ", len(crews_lines))

    #num_crews    = len(crews_lines)
    #num_incident = len(pending_lines)

 

    if num_crews < num_incident:
        print("Error: Crews < Requests")

    rows = (num_incident * 2) + num_crews + (num_crews * num_incident * 2)    
    cols = num_crews * num_incident

    printing.options['dformat'] = '%1.f'
    printing.options['width'] = -1
    
    #Creates the A matrix
    A_Temp = cvxopt.matrix (np.zeros((cols, rows)))
    A = cvxopt.matrix (np.zeros((rows, cols)))
    op.fire_limiter(A_Temp,cols,rows,num_incident)
    op.crew_limiter(A_Temp,cols,rows,num_crews,num_incident)
    op.binary_limiter(A_Temp,cols,rows,num_crews,num_incident)
    A = op.flip_matrix(A_Temp,A)

    # Creates the B matrix
    B_Temp = cvxopt.matrix (np.zeros((1, rows)))
    B = cvxopt.matrix (np.zeros((rows, 1)))
    op.create_b(B_Temp,num_crews,num_incident)
    B = op.flip_matrix(B_Temp,B)

    # Creates the C matrix
    C = cvxopt.matrix (np.zeros((num_crews * num_incident, 1)))
    circle_array = np.zeros((num_crews,num_incident))
    create_circular_array(requests,circle_array,num_crews,num_incident)
    op.create_c(C,num_crews,num_incident,circle_array)

    # Used GLPK solver to generate optimal results
    sol=cvxopt.solvers.lp(C,A,B,solver='glpk')

    # scratch  = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\scratch.csv"
    # write_all(a_Test,b_Test,c,sol,num_crews,num_incident,scratch)

    # Wrties answer to ouptut file
    write_answer(sol,output,requests,num_crews,num_incident)
