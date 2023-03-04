# https://en.wikipedia.org/wiki/Packing_problems
# https://stackoverflow.com/questions/47918792/2d-bin-packing-on-a-grid

import math
import copy
import subprocess
import numpy as np
import matplotlib.pyplot as plt      # plotting-only
import seaborn as sns                # plotting-only
from pycryptosat import Solver
np.set_printoptions(linewidth=120)   # more nice console-output

""" Constants / Input
        Example: 5 tetrominoes; no rotation """
M, N = 25, 25
polyominos = [np.array([[1,1,1,1]]),
              np.array([[1,0],[1,0], [1,1]]),
              np.array([[1,0],[1,1],[0,1]]),
              np.array([[1,1],[1,1]]),
              np.array([[1,1,1],[0,1,0]])]

""" Preprocessing
        Calculate:
        A: possible placements
        B: covered positions
        C: collisions between placements
"""
placements = []
covered = []
for p_ind, p in enumerate(polyominos):
    mP, nP = p.shape
    for x in range(M):
        for y in range(N):
            if x + mP <= M:          # assumption: no zero rows / cols in each p
                if y + nP <= N:      # could be more efficient
                    placements.append((p_ind, x, y))
                    cover = np.zeros((M,N), dtype=bool)
                    cover[x:x+mP, y:y+nP] = p
                    covered.append(cover)                           
covered = np.array(covered)

collisions = []
for m in range(M):
    for n in range(N):
        collision_set = np.flatnonzero(covered[:, m, n])
        collisions.append(collision_set)

""" Helper-function: Cardinality constraints """
# K-ARY CONSTRAINT GENERATION
# ###########################
# SINZ, Carsten. Towards an optimal CNF encoding of boolean cardinality constraints.
# CP, 2005, 3709. Jg., S. 827-831.

def next_var_index(start):
    next_var = start
    while(True):
        yield next_var
        next_var += 1

class s_index():
    def __init__(self, start_index):
        self.firstEnvVar = start_index

    def next(self,i,j,k):
        return self.firstEnvVar + i*k +j

def gen_seq_circuit(k, input_indices, next_var_index_gen):
    cnf_string = ''
    s_index_gen = s_index(next(next_var_index_gen))

    # write clauses of first partial sum (i.e. i=0)
    cnf_string += (str(-input_indices[0]) + ' ' + str(s_index_gen.next(0,0,k)) + ' 0\n')
    for i in range(1, k):
        cnf_string += (str(-s_index_gen.next(0, i, k)) + ' 0\n')

    # write clauses for general case (i.e. 0 < i < n-1)
    for i in range(1, len(input_indices)-1):
        cnf_string += (str(-input_indices[i]) + ' ' + str(s_index_gen.next(i, 0, k)) + ' 0\n')
        cnf_string += (str(-s_index_gen.next(i-1, 0, k)) + ' ' + str(s_index_gen.next(i, 0, k)) + ' 0\n')
        for u in range(1, k):
            cnf_string += (str(-input_indices[i]) + ' ' + str(-s_index_gen.next(i-1, u-1, k)) + ' ' + str(s_index_gen.next(i, u, k)) + ' 0\n')
            cnf_string += (str(-s_index_gen.next(i-1, u, k)) + ' ' + str(s_index_gen.next(i, u, k)) + ' 0\n')
        cnf_string += (str(-input_indices[i]) + ' ' + str(-s_index_gen.next(i-1, k-1, k)) + ' 0\n')

    # last clause for last variable
    cnf_string += (str(-input_indices[-1]) + ' ' + str(-s_index_gen.next(len(input_indices)-2, k-1, k)) + ' 0\n')

    return (cnf_string, (len(input_indices)-1)*k, 2*len(input_indices)*k + len(input_indices) - 3*k - 1)

def gen_at_most_n_constraints(vars, start_var, n):
    constraint_string = ''
    used_clauses = 0
    used_vars = 0
    index_gen = next_var_index(start_var)
    circuit = gen_seq_circuit(n, vars, index_gen)
    constraint_string += circuit[0]
    used_clauses += circuit[2]
    used_vars += circuit[1]
    start_var += circuit[1]

    return [constraint_string, used_clauses, used_vars, start_var]

def parse_solution(output):
    # assumes there is one
    vars = []
    for line in output.split("\n"):
        if line:
            if line[0] == 'v':
                line_vars = list(map(lambda x: int(x), line.split()[1:]))
                vars.extend(line_vars)
    return vars

def solve(CNF):
    p = subprocess.Popen(["cryptominisat5"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    result = p.communicate(input=CNF.encode())[0]
    result = result.decode()
    sat_line = result.find('s SATISFIABLE')
    if sat_line != -1:
        # solution found!
        vars = parse_solution(result)
        return True, vars
    else:
        return False, None


def solve2(CNF):
    #p = subprocess.Popen(["cryptominisat5.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    #result = p.communicate(input=CNF)[0]
    s = Solver()
    for cl in CNF:
        print(cl)
        s.add_clause(cl)
    s.add_clause(CNF)
    sat, solution = s.solve()
    if sat:
        # solution found!
        #vars = parse_solution(result)
        #return True, vars
        return True, solution
    else:
        return False, None

""" SAT-CNF: BASE """
X = np.arange(1, len(placements)+1)                                     # decision-vars
                                                                        # 1-index for CNF
Y = np.arange(len(placements)+1, len(placements)+1 + M*N).reshape(M,N)
next_var = len(placements)+1 + M*N                                      # aux-var gen
n_clauses = 0

cnf = ''                                                                # slow string appends
                                                                        # int-based would be better
# <= 1 for each collision-set
for cset in collisions:
    constraint_string, used_clauses, used_vars, next_var = \
        gen_at_most_n_constraints(X[cset].tolist(), next_var, 1)
    n_clauses += used_clauses
    cnf += constraint_string

# if field marked: one of covering placements active
for x in range(M):
    for y in range(N):
        covering_placements = X[np.flatnonzero(covered[:, x, y])]  # could reuse collisions
        clause = str(-Y[x,y])
        for i in covering_placements:
            clause += ' ' + str(i)
        clause += ' 0\n'
        cnf += clause
        n_clauses += 1

print('BASE CNF size')
print('clauses: ', n_clauses)
print('vars: ', next_var - 1)

""" SOLVE in loop -> decrease number of placed-fields until SAT """
print('CORE LOOP')
N_FIELD_HIT = M*N
while True:
    print(' N_FIELDS >= ', N_FIELD_HIT)
    # sum(y) >= N_FIELD_HIT
    # == sum(not y) <= M*N - N_FIELD_HIT
    cnf_final = copy.copy(cnf)
    n_clauses_final = n_clauses

    if N_FIELD_HIT == M*N:  # awkward special case
        constraint_string = ''.join([str(y) + ' 0\n' for y in Y.ravel()])
        n_clauses_final += N_FIELD_HIT
    else:
        constraint_string, used_clauses, used_vars, next_var = \
            gen_at_most_n_constraints((-Y).ravel().tolist(), next_var, M*N - N_FIELD_HIT)
        n_clauses_final += used_clauses

    n_vars_final = next_var - 1
    cnf_final += constraint_string
    cnf_final = 'p cnf ' + str(n_vars_final) + ' ' + str(n_clauses) + \
        ' \n' + cnf_final  # header

    status, sol = solve(cnf_final)
    if status:
        print(' SOL found: ', N_FIELD_HIT)

        """ Print sol """
        res = np.zeros((M, N), dtype=int)
        counter = 1
        for v in sol[:X.shape[0]]:
            if v>0:
                p, x, y = placements[v-1]
                pM, pN = polyominos[p].shape
                poly_nnz = np.where(polyominos[p] != 0)
                x_inds, y_inds = x+poly_nnz[0], y+poly_nnz[1]
                res[x_inds, y_inds] = p+1
                counter += 1
        print(res)

        """ Plot """
        # very very ugly code; too lazy
        ax1 = plt.subplot2grid((5, 12), (0, 0), colspan=11, rowspan=5)
        ax_p0 = plt.subplot2grid((5, 12), (0, 11))
        ax_p1 = plt.subplot2grid((5, 12), (1, 11))
        ax_p2 = plt.subplot2grid((5, 12), (2, 11))
        ax_p3 = plt.subplot2grid((5, 12), (3, 11))
        ax_p4 = plt.subplot2grid((5, 12), (4, 11))
        ax_p0.imshow(polyominos[0] * 1, vmin=0, vmax=5)
        ax_p1.imshow(polyominos[1] * 2, vmin=0, vmax=5)
        ax_p2.imshow(polyominos[2] * 3, vmin=0, vmax=5)
        ax_p3.imshow(polyominos[3] * 4, vmin=0, vmax=5)
        ax_p4.imshow(polyominos[4] * 5, vmin=0, vmax=5)
        ax_p0.xaxis.set_major_formatter(plt.NullFormatter())
        ax_p1.xaxis.set_major_formatter(plt.NullFormatter())
        ax_p2.xaxis.set_major_formatter(plt.NullFormatter())
        ax_p3.xaxis.set_major_formatter(plt.NullFormatter())
        ax_p4.xaxis.set_major_formatter(plt.NullFormatter())
        ax_p0.yaxis.set_major_formatter(plt.NullFormatter())
        ax_p1.yaxis.set_major_formatter(plt.NullFormatter())
        ax_p2.yaxis.set_major_formatter(plt.NullFormatter())
        ax_p3.yaxis.set_major_formatter(plt.NullFormatter())
        ax_p4.yaxis.set_major_formatter(plt.NullFormatter())

        mask = (res==0)
        sns.heatmap(res, cmap='viridis', mask=mask, cbar=False, square=True, linewidths=.1, ax=ax1)
        plt.tight_layout()
        plt.show()
        break

    N_FIELD_HIT -= 1  # binary-search could be viable in some cases
    # but beware the empirical asymmetry in SAT-solvers:
    #    finding solution vs. proving there is none!
