from data import filter_data, calc_pop

from pulp import *
import pandas

import pprint

area_msq = 4046.86
prob = LpProblem("GrowthOpt", LpMaximize)

# Import variables with Pandas and create

df, count = filter_data()

variable_names = ['x_{}'.format(index) for index in range(count)]
variable_dict = {name: dict(sci_name=None, cn=None, sun=None, root_depth=None) for name in variable_names}

df_index = 0
for throwaway, row in df.iterrows():

	info = variable_dict[variable_names[df_index]]

	info['sci_name'] = ''.join([x for x in row['Scientific Name'] if ord(x) < 128])
	info['cn'] = row['C:N Ratio']
	info['sun'] = row['Shade Tolerance']
	info['root'] = row['Root Depth, Minimum (inches)']
	info['growth'] = row['Growth Rate']
	info['size'] = row['Height, Mature (feet)']*0.3048

	max_population = calc_pop(area_msq, row['Height, Mature (feet)'])
	# globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population, cat="Integer")
	globals()[variable_names[df_index]] = LpVariable(info['sci_name'], 0, max_population)

	df_index += 1

## Objective
# prob += x_1 + x_2 + x_3 ...

# Growth rate weight
_fast = 1.3
_norm = 1.0
_slow = 0.6

growth_size_list = []

for index, value in enumerate(variable_names):
	temp_growth = variable_dict[value]['growth']
	temp_size = variable_dict[value]['size']

	if temp_growth == "Slow":
		temp_growth = _slow
	if temp_growth == "Moderate":
		temp_growth = _norm
	if temp_growth == "Rapid":
		temp_growth = _fast

	temp_rate = temp_growth*temp_size

	str_rate = str(temp_rate) + "*" + value

	growth_size_list.append(str_rate)


obj = " + ".join(growth_size_list)
prob += eval(obj)

## Constraints

# -----
## C:N Ratio contraint

_low = 1/23
_med = 1/41
_high = 1/91

_cn_max = 1/24
_cn_ideal = 1/30

cn_ideal_list = ['_cn_ideal*{}'.format(var) for var in variable_names]
cn_ideal_str = " + ".join(cn_ideal_list)

cn_actual_list = []

for index, value in enumerate(variable_names):
	temp_cn = variable_dict[value]['cn']
	if temp_cn == "Low":
		temp_cn = _low
	if temp_cn == "Medium":
		temp_cn = _med
	if temp_cn == "High":
		temp_cn = _high

	str_cn = str(temp_cn) + '*' + value

	cn_actual_list.append(str_cn)

cn_actual_str = " + ".join(cn_actual_list)

cn_full_str = cn_actual_str + ">=" + cn_ideal_str
prob += eval(cn_full_str)

# prob += _low*x_1 + _med*x_2 +_med*x_3 >= _cn_ideal*x_1 + _cn_ideal*x_2 + _cn_ideal*x_3
## prob += _low*x_1 + _med*x_2 +_med*x_3 <= _cn_max*x_1 + _cn_max*x_2 + _cn_max*x_3


# -----
## Sunlight contraint
# Space width by height, to maximize leaf production

# Shade intolerant, from tree to groundcover
# prob += x_1 + x_3 >= 7

# Shade intolerant groundcover condition

# Shade intermediate, limit max height to shrub
# prob += x_2 >= 7

# Shade tolerant, limit max height to groundcover



for index, value in enumerate(variable_names):
	temp_shade_tol = variable_dict[value]['sun']
	temp_height = variable_dict[value]['size']

	temp_growth = variable_dict[value]['growth']

	if temp_growth == "Slow":
		temp_growth = _slow
	if temp_growth == "Moderate":
		temp_growth = _norm
	if temp_growth == "Rapid":
		temp_growth = _fast
	
	if temp_shade_tol == "Intolerant":

		for j_index, j_value in enumerate(variable_names):
			j_temp_height = variable_dict[j_value]['size']

			j_temp_growth = variable_dict[value]['growth']

			if j_temp_growth == "Slow":
				j_temp_growth = _slow
			if j_temp_growth == "Moderate":
				j_temp_growth = _norm
			if j_temp_growth == "Rapid":
				j_temp_growth = _fast

			if j_temp_height*j_temp_growth > temp_height*temp_growth*1.5:
				height_constraint = value + "+" + j_value + "<= 0"
				prob += eval(height_constraint)


# -----
## Root depth constraint
# Occupy all laters fully
# cm^2*seeds >= total_cm^2

zero_4_depth = []
four_9_depth = []
nine_15_depth = []
fifteen_30_depth = []
thirty_more_depth = []

root_area = (area_msq/5)*0.8

for index, value in enumerate(variable_names):
	temp_root = variable_dict[value]['root']
	temp_growth = variable_dict[value]['growth']
	temp_size = variable_dict[value]['size']

	if temp_growth == "Slow":
		temp_growth = _slow
	if temp_growth == "Moderate":
		temp_growth = _norm
	if temp_growth == "Rapid":
		temp_growth = _fast

	temp_rate = temp_growth*temp_size
	str_rate = str(temp_rate) + "*" + value

	if temp_root < 4.0:
		zero_4_depth.append(str_rate)

	if temp_root >= 4.0 and temp_root < 9.0:
		four_9_depth.append(str_rate)

	if temp_root >= 9.0 and temp_root < 15.0:
		nine_15_depth.append(str_rate)

	if temp_root >= 9.0 and temp_root < 15.0:
		fifteen_30_depth.append(str_rate)

	if temp_root >= 30.0:
		thirty_more_depth.append(str_rate)

if zero_4_depth:
	zero = " + ".join(zero_4_depth) + ">=" + str(root_area)
	prob += eval(zero)

if four_9_depth:
	four = " + ".join(four_9_depth) + ">=" + str(root_area)
	prob += eval(four)

if nine_15_depth:
	nine = " + ".join(nine_15_depth) + ">=" + str(root_area)
	prob += eval(nine)

if fifteen_30_depth:
	fifteen = " + ".join(fifteen_30_depth) + ">=" + str(root_area)
	prob += eval(fifteen)

if thirty_more_depth:
	thirty = " + ".join(thirty_more_depth) + ">=" + str(root_area)
	prob += eval(thirty)


# Solve

GLPK().solve(prob)

v = prob.variables()

output = []

for solution in v:
	_value = solution.varValue	
	_name = solution.name

	if _value > 0:
		output.append((_name, round(_value)))

print('\Objective: ')
print(prob.objective)

print('\nOUTPUT: ')
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(output)
print(len(output))