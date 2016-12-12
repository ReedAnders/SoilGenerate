from . import data

from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, LpAffineExpression, lpSum, GLPK
from pulp import value as pulp_value
import pandas

import pprint

# Call GLPK with prepared LP dictionary
def optimize(df, count, filters):
	prob, prob_vars = setup(df, count, filters)

	GLPK().solve(prob)

	v = prob.variables()

	output = []

	for solution in v:
		_value = solution.varValue
		_name = ' '.join(solution.name.split('_')[1:])
		_height = None
		_light = None
		_root = None

		is_key = prob_vars.get(_name)

		if is_key:
			_height = is_key['size']
			_light = is_key['sun']
			_root = is_key['root']
			_cn = is_key['cn']

			if _value > 0:
				_name = "Scientific Name: " + _name
				_value = "Seed Count: " + str(round(_value))
				# _height = "Size: " + str(round(_height,3))
				_light = "Shade Tolerance: " + _light
				_root = "Root Depth: " + str(_root)
				_cn = "CN Ratio: " + str(round(_cn,3))
				output.append((_name, _value, _light, _root, _cn))

	return prob.objective, pulp_value(prob.objective), output

# Output result to user
def print_result(objective_value, output):
	if output:
		print('\nResult:')
		print(pulp_value(objective_value))

		print('\nSeed Count by Species: ')
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(output)
	else:
		print("SoilGenerate Error: Problem infeasible. Try removing some data filters or changing CN Target.")

# Convert cn csv value to float
def cn_str_to_float(str_value):
	float_value = 0.0
	if str_value == "Low":
		float_value = 1/23
	if str_value == "Medium":
		float_value = 1/41
	if str_value == "High":
		float_value = 1/91

	return float_value

# Convert growth csv value to float
def growth_str_to_float(str_value):
	float_value = 0.0
	if str_value == "Slow":
		float_value = 0.6
	if str_value == "Moderate":
		float_value = 1.0
	if str_value == "Rapid":
		float_value = 1.3

	return float_value

# Calculate population
def calc_pop(area, density):

	result = area/density
	return result

# Calculate density, thus plant area per ft sq
def calc_density(per_acre):
	per_foot_sq = per_acre/43560
	return per_foot_sq

# Convert nitrogen fixing csv value to int
def is_nf(nitrogen_string):
	if nitrogen_string != "None":
		return 1
	return 0

# Setup LP dictionary
def setup(df, count, filters):

	## BEGIN Create variables, constants

	area_sq = filters['area']
	_cn_target = (1/int(filters['cn_target']))

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
		info['cn'] = cn_str_to_float(row['C:N Ratio'])
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


		info['growth'] = growth_str_to_float(row['Growth Rate'])
		info['size'] = calc_density(row['Planting Density per Acre, Maximum'])
		info['pop'] = calc_pop(area_sq, info['size'])

		info['seed_price'] = row['Price Per Pound']/row['Seeds Per Pound']

		info['nitrogen'] = is_nf(row['Nitrogen Fixation'])

		df_index += 1

	# A dictionary called 'plant_vars' is created to contain the referenced Variables
	plant_vars = LpVariable.dicts("Seeds",plant_species,0)

	## END Create variables, constants

	## Objective
	# Constants in objective are the area (ft sq) occupied by each plant. 
	prob = LpProblem("GrowthOpt", LpMaximize)
	prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in plant_species]), "Objective for Size of Seed Growth"


	## Constraints

	# -----
	## C:N Ratio constraint
	# The Carbon:Nitrogen ratio in plant matter varies by plant, and an ideal ratio for plant matter decomposition is 30:1. 
	# This contraint acts as a bound on low or high carbon over all plants 

	prob += lpSum([variable_dict[i]['cn']*plant_vars[i] for i in plant_species]) >= \
			lpSum([_cn_target*plant_vars[i] for i in plant_species]), "Carbon Nitrogen Ratio Requirement"

	# -----
	## Nitrogen fixation contraint
	# Include at least one nitrogen fixing plant, because this is not an ILP, this could allow for partial plants, but this is unlikely.
	prob += lpSum([variable_dict[i]['nitrogen']*plant_vars[i] for i in plant_species]) >= 1.0, "Nitrogen fixation constraint"

	# -----
	## Root depth constraint
	# Occupy all layers by upper bound, one shallow layer by low bound
	# TODO: Fix if: work around and debug GLPK
	if root_A_plant_species:
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_A_plant_species]) <= area_sq, "Area upper bound for 0 to 4 inch root systems"
	
	if root_Bw1_plant_species:
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw1_plant_species]) <= area_sq, "Area upper bound for 4 to 9 inch root systems"
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw1_plant_species]) >= (area_sq/5), "Area lower bound for 4 to 9 inch root systems"
	
	if root_Bw2_plant_species:
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw2_plant_species]) <= area_sq, "Area upper bound for 9 to 14 inch root systems"
	
	if root_Bw3_plant_species:
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_Bw3_plant_species]) <= area_sq, "Area upper bound for 15 to 23 inch root systems"
	
	if root_E_plant_species:
		prob += lpSum([variable_dict[i]['size']*plant_vars[i] for i in root_E_plant_species]) <= area_sq, "Area upper bound for over 23 inch root systems"

	# -----
	## Budget contraint  
	if filters['budget']:
		prob += lpSum([variable_dict[i]['seed_price']*plant_vars[i] for i in plant_species]) <= filters['budget'], "Budget contraint in USD"

	# Return 
	return prob, variable_dict
