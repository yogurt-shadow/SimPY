from typing import List
import numpy as np

class range:
   def __init__(self, l, u):
      self.lower_inf = (l == None)
      self.lower = l
      self.upper_inf = (u == None)
      self.upper = u

class variable:
   def __init__(self, name: str, rg: range):
      self.name = name
      self.range = rg

class constraint:
   # rela: >=, <=, ==
   def __init__(self, coeff: List[float], rela: str, rhs: float):
      self.coeff = coeff
      self.rela = rela
      self.rhs = rhs

class solver:
   def __init__(self):
      self.var_list = []
      self.cons_list = []

   def register_constraint(self, cons: constraint):
      self.cons_list.append(cons)

   def register_var(self, v: variable):
      self.var_list.append(v)

   def get_nvars(self) -> int:
      return len(self.var_list)

   def get_ncons(self) -> int:
      return len(self.cons_list)

   """
   Change to standard LP format
   1. change vars into standard vars ([0, +oo))
   """
   def normalize(self):
      self.normalize_vars()
      self.normalize_constraints()
      self.generate_matrix()
   
   """
   change vars according to their range
   """
   def normalize_vars(self):
      self.new_vars = 0
      self.sub_map = [{} for i in range(self.get_nvars())]
      for v in self.var_list:
         self.normalize_var(v)
   
   """
   1. [0, +oo): do nothing
   2. free: x = x' - x''
   3. [a, +oo]: x = x' + a
   4. [a, b]: case 3, add cons x <= b
   """
   def normalize_var(self, v):
      # case 1: (-oo, +oo)
      if v.range.lower_inf == True and v.range.upper_inf == True:
         id1, id2 = self.new_vars, self.new_vars + 1
         self.new_vars += 2
         # x = x' - x''
         self.sub_map[v] = {id1: 1, id2: -1}
      # case 2: [a, +oo)
      elif v.range.lower_inf == False and v.range.upper_inf == True:
         # x = x' + a
         id = self.new_vars
         self.new_vars += 1
         self.sub_map[v] = {id: 1, -1: v.range.lower}
      # case 3: (-oo, a]
      elif v.range.lower_inf == True and v.range.upper_inf == False:
         # x = -x' + a
         id = self.new_vars
         self.new_vars += 1
         self.sub_map[v] = {id: -1, -1: v.range.upper}
      # case 4: [a, b]
      else:
         # x = x' + a
         # add cons: x <= b
         id = self.new_vars
         self.new_vars += 1
         self.sub_map[v] = {id: 1, -1: v.range.lower}
         cons_coeff = [1 if i == v else 0 for i in range(self.get_nvars())]
         self.register_constraint(constraint(cons_coeff, "<=", v.range.upper))

   def normalize_constraints(self):
      self.cons_map = [{} for i in range(self.get_ncons())]
      for i in range(self.get_ncons()):
         self.normalize_constraint(i)

   def generate_cons_map(self, cons: constraint) -> dict:
      res = {}
      for v1 in range(len(cons.coeff)):
         if cons.coeff[v1] == 0:
            continue
         else:
            for v2, v2_coeff in self.sub_map[v1]:
               if v2 not in res.keys():
                  res[v2] = 0
               res[v2] += cons.coeff[v1] * v2_coeff
      return res

   def normalize_constraint(self, idx):
      cons = self.cons_list[idx]
      self.cons_map[idx] = self.generate_cons_map(cons)
      if cons.rela == "==":
         return
      elif cons.rela == ">=":
         # cons >= rhs
         # cons - x == rhs
         id = self.new_vars
         self.new_vars += 1
         self.cons_map[idx][id] = -1
      elif cons.rela == "<=":
         # cons <= rhs
         # cons + x == rhs
         id = self.new_vars
         self.new_vars += 1
         self.cons_map[idx][id] = 1
      else:
         raise ValueError('invalid constraint relation %r' % cons.rela)
      
   def generate_matrix(self):
      self.rhs = np.array()
      coeffs = [[0 for i in range(self.new_vars)] for j in range(len(self.cons_list))]
      for i in range(len(self.cons_list)):
         for v_id, v_coeff in self.cons_map[i]:
            coeffs[i][v_id] = v_coeff
            self.rhs.append(self.cons_list[i].rhs)
      self.coeff_matrix = np.mat(coeffs)
      self.rhs = self.rhs.reshape((-1, 1))

   def solve(self):
      self.normalize()
