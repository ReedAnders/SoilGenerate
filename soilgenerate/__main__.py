import argparse

from soilgenerate import data, core

def main():
	"""The main routine."""
	parser = argparse.ArgumentParser()

	parser.add_argument("--area", required=True, type=int, help="Area of land for planting (square feet)")

	parser.add_argument("--soil_texture", required=True, type=str, help="Soil texture of area as combinations of: Course, Medium, or Fine")
	soil_options = set(['course','med-course','med','med-fine','fine'])

	parser.add_argument("--hardiness", required=True, type=int, help="Minimum temperature hardiness of area (fahrenheit)")

	parser.add_argument("--percip_min", required=True, type=int, help="Minimum precipitation of area (inches)")

	parser.add_argument("--percip_max", required=False, type=int, help="Maximum precipitation of area (inches)")

	parser.add_argument("--cn_ratio", default='low-med-high', type=str, help="Filter for C:N Ratio in plants. Value 'low-med' excludes high ratio \
	plants; value 'low-med-high' includes all ratio plants. Low = 23:1, Med = 41:1, High = 91:1")
	ratio_options = set(['low-med','low-med-high'])

	parser.add_argument("--cn_target", default=30, type=int, help="Filter for target carbon amount in C:N Ratio")

	parser.add_argument("--animal_browse", default='low-med-high', type=str, help="Filter for animal browse palatability in plants. \
		value 'low' includes only low browse plants.; value 'low-med' excludes high browse plants; value 'low-med-high' includes all plants.")
	browse_options = set(['low','low-med','low-med-high'])

	args = vars(parser.parse_args())

	if args['soil_texture'] not in soil_options:
		raise ValueError('Soil type must be of either ' + str(soil_options))

	if args['cn_ratio'] not in ratio_options:
		raise ValueError('Ratio type must be of either ' + str(ratio_options))

	if args['animal_browse'] not in browse_options:
		raise ValueError('Animal browse type must be of either ' + str(animal_browse))


	filtered_data, filter_count = data.filter(args)

	try:
		objective, growth, seeds = core.optimize(filtered_data, filter_count, args)
		core.print_result(growth, seeds)
	except Exception as e:
		print(e)
		objective, variables = core.setup(filtered_data, filter_count, args)
		print('SoilGenerate Error: Problem infeasible with only {} plant species available for optimization. Try removing some data filters.'.format(len(variables)))
		# print('Error: Problem infeasible. The data filters are likely too strict, and not enough plant species are available as variables. Try removing some data filters.')
	else:
		pass
	finally:
		pass


if __name__ == "__main__":
	main()
