import numpy as np
import pandas as pd
from plotnine import *
from datetime import *
from pulp import *
from random import *
from itertools import *

good_data = pd.read_csv('UNDERSCORE DEMAND DATA SOUTH STORES WD.csv')
new_good_data = pd.read_csv("UNDERSCORE DEMAND DATA SOUTH STORES WD.csv", index_col=0)

routes = []
pallets = []

stores_dict = good_data.set_index('Name')['average_demand'].to_dict()

# iterates through to make 10 routes (can be increased)
for j in range(90):
    prob = LpProblem("Route Creation", LpMaximize)

    stores = LpVariable.dicts('', good_data['Name'], lowBound=0, upBound=1, cat='Integer')
    # each store has value 0 or 1 (1 means visited in route)

    prob += lpSum([stores[i] for i in good_data['Name']]), 'Total stores visited'
    # maximising total of all these 0s and 1s (maximising number of stores reached)

    prob += lpSum([stores[i]*new_good_data.loc[i]['average_demand'] for i in good_data['Name']]) <= 20
    # each store's value times its demand gives us total demand for each route, must be less than arbitrary truck
    # capacity eg. 20

    prob += lpSum([stores[i] for i in good_data['Name']]) >= 2
    # limit routes to having at least 3 stores incl. distribution

    prob += lpSum(stores['Distribution_South']) >= 1
    # must include south distribution centre

    prob += lpSum(stores['Distribution_North']) >= 1
    # add if considering northern distribution centre

    for route in routes:
        prob += lpSum([stores[i] for i in route]) <= len(route)-1
        # ensures we dont make the same route twice if u think about it it works trust

    prob.writeLP("Routes.lp")

    prob.solve()

    if LpStatus[prob.status] == 'Infeasible':
        print("Stopped at:", j)
        break

    names = []
    for v in prob.variables():
        if v.varValue == 1:
            names.append(v.name.strip('_'))
        # creates a list of stores visited in route we just made

    for shuffle in permutations(names):
        routes.append(list(shuffle))
    # appends that list to bigger list of all routes ever made


for route in routes:
    pallets.append(sum(stores_dict[store] for store in route))

#for v in prob.variables():

    #print(v.name, "=", v.varValue)

# creates dataframe of all routes made
unopt_routes = pd.DataFrame(routes)
unopt_routes.fillna(0, inplace=True)

index = [i for i in range(len(unopt_routes))]
unopt_routes['Route Number'] = index
unopt_routes['Pallets'] = pallets

##########################################################
# This section calculates total time taken by each route

cost_list = []

# loops through list of routes
for j in range(len(unopt_routes['Route Number'])):
    cost = 0
    i = 0

    while i < len(unopt_routes.iloc[j][:])-3:
        # i indexes stores in each route
        current_node = unopt_routes.iloc[j][i]
        next_node = unopt_routes.iloc[j][i+1]

        if type(current_node) != str:
            break

        # cost is the sum of the trip between each store
        cost += new_good_data.loc[current_node][next_node]
        i += 1

    # calculates cost of travelling from last store back to beginning    
    cost += new_good_data.loc[unopt_routes.iloc[j][i-1]][unopt_routes.iloc[j][0]]
    cost_list.append(cost)

# calculates total time - travel and unloading 
total_time = [cost_list[x] + (pallets[x]*600) for x in range (len (cost_list))]  

# add Travel Time and Total Time columns to data frame
unopt_routes['Travel Time'] = pd.Series(cost_list)
unopt_routes['Total Time'] = pd.Series(total_time)

# write routes to .csv file
unopt_routes.to_csv('WD_SOUTH.csv')
'''
##############################################
# This section eliminates routes based on time taken



problem = LpProblem("Route Selection", LpMinimize)

routes = LpVariable.dicts('Route', unopt_routes.loc[:]['Route Number'], lowBound=0, upBound=1, cat='Integer')



problem += lpSum([[routes[i]*unopt_routes.iloc[i]['Total Time']
         + routes[i]*unopt_routes.iloc[i]['Pallets']*10] for i in unopt_routes['Route Number']]), 'Total time per route'

for i in unopt_routes['Route Number']:

    if unopt_routes.iloc[i]['Total Time'] + unopt_routes.iloc[i]['Pallets']*10 > 13500:
        problem += routes[i] == 0

for store in good_data['Name']:

    if store == 'Distribution_North':
        continue

    coefficients = []
    for i in unopt_routes.loc[:]['Route Number']:

        for node in unopt_routes.loc[i][:]:

            if store == node:
                coefficients.append(i)

    problem += lpSum(routes[i] for i in coefficients) >= 1

problem.writeLP("Feasible_Routes.lp")

problem.solve()

for v in problem.variables():

    if v.varValue == 1:
        print(v.name)
        print(unopt_routes.loc[int(v.name.removeprefix('Route_'))][:])
        print('Loading Time:', v.varValue)
'''        
