
#cvxopt.org/userguide/coneprog.html?highlight=solvers#cvxopt.solvers.lp

import cvxopt
from cvxopt import printing
import numpy as np

# Creates first 1/3 of the A Matrix
# Assignes constaint rows so that each fire has a crew assigned to it
# creates two rows since we cannot directly create an = constaint
# first row is positive and second row is negative
def fire_limiter(given_matrix,rows,cols,num_incident):
    for i in range(rows):
        for j in range(num_incident):
            val = (j - i) % num_incident
            if (val == 0):
                val = 1
            else:
                val = 0
            given_matrix[i,j] = val
            given_matrix[i,j + num_incident] = val * -1
# Creates 2/3 of the A Matrix
# Limits each crew to only being allowed to go to one request
# Creates a <= constaint since not every crew must go to a request
def crew_limiter(given_matrix,rows,cols,num_crews,num_incident):
    start = num_incident * 2
    row_counter = 0

    for i in range(start, start + num_crews):
        counter = 0
        while(counter < num_incident):
            given_matrix[row_counter,i] = 1
            counter += 1
            row_counter += 1

# Creates 3/3 of the A Matrix
# Limites each crew to a binary variable
# this forces the results of the optimization program to be boolean in nature
# creates a positive and negative row to bound from 0 and 1
def binary_limiter(given_matrix,rows,cols,num_crews,num_incident):
    
    start = num_incident * 2 + num_crews
    row_counter = 0

    for i in range(start, cols - 1):
        counter = 0
        while(counter < 1 and row_counter < rows):
            given_matrix[row_counter,i] = 1
            given_matrix[row_counter,i + num_crews * num_incident] = -1
            counter += 1
            row_counter += 1
            
# Creates the whole B matrix that is used as the answers column for the optimzation
def create_b(given_matrix,num_crews,num_incident):
    index = 0

    for j in range(num_incident):
        given_matrix[0,j] = 1
        given_matrix[0,j + num_incident] = -1
        index += 1
    for j in range(num_incident * 2, num_incident * 2 + num_crews):
        given_matrix[0,j] = 1

    for j in range(num_incident * 2 + num_crews, num_incident * 2 + num_crews + num_crews * num_incident):
        given_matrix[0,j] = 1

# Since the matricies are created sideways we used this functuon to flip them for the optimzation program 
# returns a new matrix with the correct dimensions
def flip_matrix(old_matrix,new_matrix):
    old_row = old_matrix.size[0]
    old_col = old_matrix.size[1]
    
    new_row = new_matrix.size[0]
    new_col = new_matrix.size[1]

    for i in range(old_row):
        for k in range(old_col):
            new_matrix[k,i] = old_matrix[i,k]
    return new_matrix

# Takes a 2d array
# Each row is a given crew and their distance to every fire
# if the distance is < 1 it is assigned 5,000 and essentially ignored in the optimization 
def create_c(given_matrix,num_crews,num_incident,circle_array):
    counter = 0
    for i in circle_array:
        for j in i:
            if j < 0:
                j = 5000
            given_matrix[counter,0] = j
            counter += 1
    return given_matrix


if __name__ == '__main__':

    #Each row is an entire variables Column from the optimzation equation and contraints
    #A1
    #A2
    #C1
    #C2
    #D1
    #D2
                            #Fire one crew(4)        #one crew only(3) #Binary variables only  (12)
    ''' A = cvxopt.matrix([ [1.0, 0.0,-1.0, 0.0,     1.0, 0.0, 0.0,    1.0, 0.0 ,0.0 ,0.0 ,0.0 ,0.0,-1.0 ,0.0 ,0.0 ,0.0 ,0.0 ,0.0],  
                            [0.0, 1.0, 0.0,-1.0,     1.0, 0.0, 0.0,    0.0 ,1.0 ,0.0, 0.0 ,0.0 ,0.0, 0.0,-1.0 ,0.0 ,0.0 ,0.0 ,0.0], 
                            [1.0, 0.0,-1.0, 0.0,     0.0, 1.0, 0.0,    0.0 ,0.0 ,1.0 ,0.0 ,0.0, 0.0, 0.0 ,0.0,-1.0 ,0.0 ,0.0 ,0.0], 
                            [0.0, 1.0, 0.0,-1.0,     0.0, 1.0, 0.0,    0.0 ,0.0 ,0.0 ,1.0 ,0.0 ,0.0, 0.0, 0.0 ,0.0,-1.0 ,0.0 ,0.0], 
                            [1.0, 0.0,-1.0, 0.0,     0.0, 0.0, 1.0,    0.0 ,0.0 ,0.0 ,0.0 ,1.0 ,0.0, 0.0 ,0.0 ,1.0, 0.0,-1.0 ,0.0], 
                            [0.0, 1.0, 0.0,-1.0,     0.0, 0.0, 1.0,    0.0 ,0.0 ,0.0 ,0.0 ,0.0 ,1.0, 0.0 ,0.0 ,0.0 ,0.0 ,0.0,-1.0] ] )
    #------------------------------------------------------------------------------------------------------------------------------------                    
    b = cvxopt.matrix(      [1.0,1.0, -1.0,-1.0,     1.0, 1.0, 1.0,    1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] )
    '''

    num_crews = 5
    num_incident = 5
    
    rows = (num_incident * 2) + num_crews + (num_crews * num_incident * 2)    
    cols = num_crews * num_incident

    printing.options['dformat'] = '%1.f'
    printing.options['width'] = -1
    
    A_Test = cvxopt.matrix (np.zeros((cols, rows)))

    a_Test = cvxopt.matrix (np.zeros((rows, cols)))

    fire_limiter(A_Test,cols,rows,num_incident)
    crew_limiter(A_Test,cols,rows,num_crews,num_incident)
    binary_limiter(A_Test,cols,rows,num_crews,num_incident)

    a_Test = flip_matrix(A_Test,a_Test)
    print(a_Test)
    
    B_Test = cvxopt.matrix (np.zeros((1, rows)))
    b_Test = cvxopt.matrix (np.zeros((rows, 1)))
    create_b(B_Test,num_crews,num_incident)

    b_Test = flip_matrix(B_Test,b_Test)
    print(b_Test)
    #c = cvxopt.matrix([ 10.0, 5.0, 30.0, 30.0, 15.0, 0.0 ])
    c = cvxopt.matrix([ 10.0, 5.0, 15.0, 20.0, 0,
                        0.0, 23.0, 9.0, 3.0, 5,
                        7.0,0.0,12.0,6.0, 7,
                        10.0,20.0,3.0,0.0, 8,
                         5.0,7.0,0.0,3.0, 9 ])
    print(c)
    sol=cvxopt.solvers.lp(c,a_Test,b_Test,solver='glpk')
    print(sol['x'])
