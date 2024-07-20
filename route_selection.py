import numpy as np
import pandas as pd 
from pulp import *

df = pd.read_csv('DdataWD.csv')
'''
For the purpose of this code:
Route 1 = A, B ——— Demand A: 4, Demand B: 6 - Pallets: 10
Route 2 = B, C ——— Demand C: 5 - Pallets: 11
Route 3 = A, D ——— Demand D: 7 - Pallets: 11
Route 4 = C, E ——— Demand E: 5 - Pallets: 10
Route 5 = A, E ——— Pallets: 9
Route 6 = B, E ——— Pallets: 11

Note: 
    - Assuming the durations to travel between two nodes 
      is the same regardless of direction.
    - All nodes must be visited only once
    - For the actual implem, each route should be a complete route
      e.g Route 1 = A -> C -> D -> E -> A
    - Probaly have to use 233 OOP for node and arcs and network
'''

# list of all nodes - this should be all the stores
Nodes = ['A', 'B', 'C', 'D', 'E']

# list of the smaller routes in one complete route? 
Routes = ['1', '2', '3', '4', '5', '6']

# from and to nodes of each route - indexed by Routes
From = pd.Series(['A', 'B', 'A', 'C', 'A', 'B'], index = Routes)
To = pd.Series(['B', 'C', 'D', 'E', 'E', 'E'], index = Routes)

# Durations - should be taken from WarehouseDurations.csv - summation likely needed
Durations = pd.Series([6000, 10000, 3000, 5200, 2023, 1221], index = Routes)

# Combined demand of all nodes per small route - from one of the processed csv files
Pallets = pd.Series([10, 11, 11, 10, 9, 11], index = Routes)

# Unloading time - from number of pallets per route, 10 mins per pallet
# PERFORM THIS CALCULATION IN R?
unload_time = []
for i in Pallets:
    unload = i*600
    unload_time.append(unload)
Unload = pd.Series(unload_time, index = Routes)

# Cost of each route - from durations (truck driving time)
cost = []
for i in Durations:
    cost.append(i*175/3600)

Cost = pd.Series(cost, index = Routes)
RoutesData = pd.DataFrame({'From': From,
                           'To': To,
                           'Durations': Durations,
                           'Pallets': Pallets,
                           'Unload': Unload,
                           'Cost': Cost})
print(RoutesData)
'''
arcs = []
for i in range(len(nodes)-1):
    current_node = nodes[i]
    next_node = nodes[i+1]
    arc_w = df.loc[current_node][next_node]
    arc = [current_node, next_node, arc_w]
    arcs.append(arc)
'''
trucks = 16
prob = LpProblem("RouteSelection", LpMinimize)
routes = LpVariable.dicts("Route",Routes,0,1,LpInteger)

# Objective function
prob += lpSum([Cost[i]*routes[i] for i in Routes]), "Minimise costs"

# ==== CONSTRAINTS ==== #

# 4 hours per route - incl. driving and unloading
prob += lpSum([Durations[i]*routes[i]+Unload[i] for i in Routes]) <= 14400, "Time allowed per truck's route"

# Number of trucks 
prob += lpSum([routes[i] for i in Routes]) <= trucks, "Trucks Fleet"

# Visit each node only once constraint
for j in Nodes:
    prob += lpSum([routes[i] for i in routes if (RoutesData.loc[i]['From'] is j) or (RoutesData.loc[i]['To'] is j)]) == 1, 'Node' + j

prob.writeLP("RouteSelection.lp")
prob.solve()

print("Status:", LpStatus[prob.status])
print("Total time taken =")



