import numpy as np

def simplex(A, b, c):
    nVars, nCons = len(c), len(A)
    bvars, nbvars = [i for i in range(nCons, nVars)], [i for i in range(0, nCons)]
    iteration, z = 0, 0
    while True:
        print("====================== Iteration: %d ======================" % iteration)
        iteration += 1
        B, N = A[:, bvars], A[:, nbvars]
        xb = np.matmul(np.linalg.inv(B), b)
        cb = c[bvars]
        z = np.matmul(cb, xb)
        print("objective: ", z)
        in_var, rc_min = None, None
        # obtain in non-basic variable 
        for v in nbvars:
            rc = c[v] - np.matmul(cb, np.matmul(np.linalg.inv(B), A[:, v]))
            if rc_min == None or rc < rc_min:
                rc_min, in_var = rc, v
        if rc_min == None or rc_min >= 0:
            break
        print("in nbvar: ", in_var)
        # obtain out basic variable
        y = np.matmul(np.linalg.inv(B), A[:, in_var])
        step = [xb[i]/y[i] if y[i] > 0 else float('inf') for i in range(len(y))]
        out_var = bvars[step.index(min(step))]
        print("out_var: ", out_var)
        bvars.append(in_var)
        bvars.remove(out_var)
        nbvars.append(out_var)
        nbvars.remove(in_var)
    print("====================== Finish ======================")
    print("best solution: ", xb)
    print("best bvars: ", bvars)
    print("best solution: ", z)


if __name__ == "__main__":
    A = np.matrix([[-1, 2, 1, 0], [3, -1, 0, 1]])
    b = np.array([1, 3]).reshape(-1, 1)
    c = np.array([-1, 1, 0, 0])
    simplex(A, b, c)
    """
    Homework

    min -x1 - x2
    s.t. - x1 + 2 x2 + x3 = 1
         3 x1 - x2   + x4 = 3
         x1, x2, x3, x4 >= 0
    """
    HA = np.array([[-1, 2, 1, 0], [3, -1, 0, 1]])
    Hb = np.array([1, 3]).reshape(-1, 1)
    Hc = np.array([-1, -1, 0, 0])
    simplex(HA, Hb, Hc)