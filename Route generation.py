import pandas as pd

df = pd.read_csv("DEMAND DATA EAST AND CENTRAL STORES WD.csv")
current_route = ['Distribution South']

# truck
truck = 0

# makes list of stores and demands
stores = df['Name'].tolist()
demand = df['average_demand'].tolist()

stores.remove('Distribution South')
stores.remove('Distribution North')

routes = [[]]

# makes dictionary of stores and demands
stores_dict = df.set_index("Name")["average_demand"].to_dict()

# idk tbh i found this bit on google but it makes all possible routes
for element in stores:
    for sub_set in routes.copy():
        new_sub_set = sub_set + [element]
        routes.append(new_sub_set)

acceptable_routes = [[]]

# selects routes that have a demand of 20 or less
for route in routes:
    route_demand = sum(stores_dict.get(item) for item in route)
    if route_demand <= 20:
        # ensures it starts and finishes with the distribution center
        route.insert(0, 'Distribution South')
        route.append('Distribution South')
        acceptable_routes.append(route)
print(acceptable_routes)



