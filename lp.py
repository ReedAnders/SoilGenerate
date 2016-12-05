from data import filter_data, calc_pop

from pulp import LpProblem, LpVariable, LpMaximize, LpAffineExpression, lpSum, GLPK
from pulp import value as pulp_value
import pandas

import pprint

area_msq = 43560

# Import variables with Pandas and create

df, count = filter_data()

variable_names = ['x_{}'.format(index) for index in range(count)]
variable_dict = {name: dict(sci_name=None, cn=None, sun=None, root=None) for name in variable_names}

plant_species = []
root_A_plant_species, root_Bw1_plant_species, root_Bw2_plant_species, root_Bw3_plant_species, root_E_plant_species = [],[],[],[],[]

df_index = 0
for throwaway, row in df.iterrows():

	info = variable_dict[variable_names[df_index]]

	sci_name = ''.join([x for x in row['Scientific Name'] if ord(x) < 128])
	variable_dict[sci_name] = variable_dict.pop(variable_names[df_index])
	plant_species.append(sci_name)

	info['sci_name'] = ''.join([x for x in row['Scientific Name'] if ord(x) < 128]) 

	temp_cn = row['C:N Ratio']
	if temp_cn == "Low":
		info['cn'] = 1/23
	if temp_cn == "Medium":
		info['cn'] = 1/41
	if temp_cn == "High":
		info['cn'] = 1/91

	info['sun'] = row['Shade Tolerance']

	temp_root = row['Root Depth, Minimum (inches)']
	info['root'] = temp_root
	
	if temp_root < 4.0:
		root_A_plant_species.append(sci_name)

	if temp_root >= 4.0 and temp_root < 9.0:
		root_Bw1_plant_species.append(sci_name)

	if temp_root >= 9.0 and temp_root < 15.0:
		root_Bw2_plant_species.append(sci_name)

	if temp_root >= 15.0 and temp_root < 23.0:
		root_Bw3_plant_species.append(sci_name)

	if temp_root >= 23.0:
		root_E_plant_species.append(sci_name)


	info['growth'] = row['Growth Rate']
	temp_growth = info['growth']

	if temp_growth == "Slow":
		temp_growth = 0.6
	if temp_growth == "Moderate":
		temp_growth = 1.0
	if temp_growth == "Rapid":
		temp_growth = 1.3

	info['size'] = (row['Height at Base Age, Maximum (feet)']**1.5)

	info['pop'] = calc_pop(area_msq, info['size'])
	# globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population, cat="Integer")
	# globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population)

	df_index += 1

# A dictionary called 'plant_vars' is created to contain the referenced Variables
plant_vars = LpVariable.dicts("Seeds",plant_species,0)

## Objective
prob = LpProblem("GrowthOpt", LpMaximize)
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in plant_species]), "Total Expected Growth of All Seeds"

## Constraints

# -----
## C:N Ratio contraint

_cn_ideal = 1/30

# prob += lpSum([variable_dict[i]['cn']*plant_vars[i] for i in plant_species]) >= \
# 		lpSum([_cn_ideal*plant_vars[i] for i in plant_species]), "Carbon Nitrogen Ratio Requirement"

# -----
## Sunlight contraint
# Space width by height, to maximize leaf production

# for key in plant_species:
# 	species_dict = variable_dict.get(key)

# 	for index, compare in enumerate(plant_species):
# 		compare_dict = variable_dict.get(compare)

# 		if species_dict and compare_dict:
# 			if species_dict['sun'] == 'Intolerant':
# 				# import pdb; pdb.set_trace()
# 				if species_dict['size'] < compare_dict['size']:
# 					gname = key + ' contraint ' + str(index)
# 					prob += LpAffineExpression(plant_vars[key] and plant_vars[compare]) == 0, gname

# -----
## Root depth constraint
# Occupy all laters by upper bound

prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_A_plant_species]) <= area_msq, "Area upper bound for 0 to 4 inch root systems"
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw1_plant_species]) <= area_msq, "Area upper bound for 4 to 9 inch root systems"
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw1_plant_species]) >= (area_msq/5), "Area lower bound for 4 to 9 inch root systems"
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw2_plant_species]) <= area_msq, "Area upper bound for 9 to 14 inch root systems"
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw3_plant_species]) <= area_msq, "Area upper bound for 15 to 23 inch root systems"
prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_E_plant_species]) <= area_msq, "Area upper bound for over 23 inch root systems"

# Solve

# NOTES:
# Querk with browsing and root depth. Including 'high' browse makes root opt infeasible


GLPK().solve(prob)

v = prob.variables()


output = []

for solution in v:
	_value = solution.varValue
	_name = ' '.join(solution.name.split('_')[1:])
	_height = None
	_light = None
	_root = None

	is_key = variable_dict.get(_name)

	if is_key:
		_height = is_key['size']
		_light = is_key['sun']
		_root = is_key['root']

		if _value > 0:
			output.append((_name, round(_value), _height, _light, _root))


print('\nObjective: ')
print(prob.objective)

print('\nResult:')
print(pulp_value(prob.objective))

print('\nOUTPUT: ')
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(output)
print(len(output))