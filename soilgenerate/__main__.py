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

	parser.add_argument("--percip_max", required=True, type=int, help="Maximum precipitation of area (inches)")

	parser.add_argument("--cn_ratio", default='low-med-high', type=str, help="Filter for C:N Ratio in plants. Value 'low-med' excludes high ratio \
	plants; value 'low-med-high' includes all ratio plants. Low = 23:1, Med = 41:1, High = 91:1")
	ratio_options = set(['low-med','low-med-high'])

	parser.add_argument("--cn_target", default=30, type=int, help="Filter for target carbon amount in C:N Ratio")

	parser.add_argument("--animal_browse", default='low-med-high', type=str, help="Filter for animal browse palatability in plants. \
		value 'low' includes only low browse plants.; value 'low-med' excludes high browse plants; value 'low-med-high' includes all plants.")
	browse_options = set(['low','low-med','low-med-high'])

	parser.add_argument("--growth_rate", required=False, type=str, help="Filter for growth rate in plants. \
		value 'rapid' includes only low rapid plants.; value 'rapid-moderate' excludes slow plants. Growth rate is otherwise weighted in optimization")
	growth_options = set(['rapid','rapid-moderate'])

	parser.add_argument("--invasive", required=False, default=False, type=bool, help="Filter invasive plants")

	parser.add_argument("--full_shade", required=False, default=False, type=bool, help="Filter for only full shade plants")

	parser.add_argument("--full_sun", required=False, default=False, type=bool, help="Filter for only full sun, low height plants; eg: an open field. ")

	parser.add_argument("--max_height", required=False, type=float, help="Filter plants by maximum height")

	parser.add_argument("--known_supplier", required=False, default=False, type=bool, help="Filter plants for those with known supplier (Sheffield's Seeds)")

	parser.add_argument("--budget", required=False, default=False, type=int, help="Budget contraint in USD")

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
		if seeds:
			core.print_result(growth, seeds)
		else: 
			objective, variables = core.setup(filtered_data, filter_count, args)
			print('SoilGenerate Error: Problem infeasible with only {} plant species available for optimization. Try removing some data filters or changing CN Target.'.format(len(variables)))
	except Exception as e:
		if type(e).__name__ == "PulpSolverError":
			objective, variables = core.setup(filtered_data, filter_count, args)
			print('SoilGenerate Error: Problem infeasible with only {} plant species available for optimization. Try removing some data filters or changing CN Target.'.format(len(variables)))
		else:
			print(e)


if __name__ == "__main__":
	main()
