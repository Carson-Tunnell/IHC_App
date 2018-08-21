
#cvxopt.org/userguide/coneprog.html?highlight=solvers#cvxopt.solvers.lp

import cvxopt

A = cvxopt.matrix([ [-1.0, -1.0, 0.0, 1.0], [1.0, -1.0, -1.0, -2.0] ])
b = cvxopt.matrix([ 1.0, -2.0, 0.0, 4.0 ])
c = cvxopt.matrix([ 2.0, 1.0 ])
sol=cvxopt.solvers.lp(c,A,b)

'''print("A Code: " , A.typecode)
print(A.size[1])
print(type(A))
'''

print(sol['x'])

'''

c = cvxopt.matrix([-4., -5.])
G = cvxopt.matrix([[2., 1., -1., 0.], [1., 2., 0., -1.]])
h = cvxopt.matrix([3., 3., 0., 0.])
sol = cvxopt.solvers.lp(c, G, h)
print(sol['x'])
'''