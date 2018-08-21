import numpy as np
from scipy.optimize import minimize
       #A1 A2 B1 B2 C1 C2 D1 D2
dist = [10,5 ,15,15,30,30,15,00]
        #A     #B    #C     #D
crews = [(0,0),(0,0),(0,0),(0,0)]

def objective(x):
    return  x[0]*dist[0] + x[1]*dist[1] + \
            x[2]*dist[2] + x[3]*dist[3] + \
            x[4]*dist[4] + x[5]*dist[5] + \
            x[6]*dist[6] + x[7]*dist[7]

def constraintA(x):
    return x[0] + x[1] - 1.0

def constraintB(x):
    return x[2] + x[3] - 1.0

def constraintC(x):
    return x[4] + x[5] - 1.0

def constraintD(x):
    return x[6] + x[7] - 1.0    

def constraint1(x):
    print('A1 = ' + str(x[0]))
    print('B1 = ' + str(x[2]))
    print('C1 = ' + str(x[4]))
    print('D1 = ' + str(x[6]))
    return (x[0] + x[2] + x[4] + x[6]) - 1.0

def constraint2(x):
    
    return (x[1] + x[3] + x[5] + x[7]) - 1.0

# initial guesses
n = 8
x0 = np.zeros(n)
x0[0] = 1.0
x0[1] = 0.0
x0[2] = 0.0
x0[3] = 0.0
x0[4] = 0.0
x0[5] = 0.0
x0[6] = 0.0
x0[7] = 1.0

# show initial objective
print('Initial Objective: ' + str(objective(x0)))

# optimize
b = (0,1)
bnds = (b, b, b, b, b, b, b, b)
con1 = {'type': 'ineq', 'fun': constraintA} 
con2 = {'type': 'ineq', 'fun': constraintB} 
con3 = {'type': 'ineq', 'fun': constraintC} 
con4 = {'type': 'ineq', 'fun': constraintD} 
con5 = {'type': 'eq', 'fun': constraint1}
con6 = {'type': 'eq', 'fun': constraint2}

cons = ([con1,con2,con3,con4,con5,con6])
solution = minimize(objective,x0,method='SLSQP',\
                    bounds=bnds,constraints=cons,options={'ftol': 1.0})
x = solution.x

# show final objective
print('Final Objective: ' + str(objective(x)))

# print solution
print('Solution')
print(solution)

print('A1 = ' + str(x[0]))
print('B1 = ' + str(x[2]))
print('C1 = ' + str(x[4]))
print('D1 = ' + str(x[6]))

print('A2 = ' + str(x[1]))
print('B2 = ' + str(x[3]))
print('C2 = ' + str(x[5]))
print('D2 = ' + str(x[7]))

print("1's = " + str(x[0] + x[2] + x[4] + x[6]))
print("2's = " + str(x[1] + x[3] + x[5] + x[7]))