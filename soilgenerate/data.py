import pandas as pd
import numpy as np

# Filter csv data based on application args
def filter(filter_args):

	# Read in csv data
	df = pd.read_csv('soilgenerate/data/12072016_plants_sheff.csv', encoding="utf-8")

	## BEGIN Default Filters
	# Filter nan
	is_not_nan = pd.notnull(df['Growth Rate'])
	df = df[is_not_nan]

	is_not_nan = pd.notnull(df['Planting Density per Acre, Maximum'])
	df = df[is_not_nan]

	# Filter seed
	if filter_args['known_supplier'] or filter_args['budget']:
		is_aval = df['Sheffields Aval'] == True
	else:
		is_aval = df['Commercial Availability'] == "Routinely Available"

	df = df[is_aval]

	##END Default Filters

	# Filter invasive
	if not filter_args['invasive']:
		is_not_invasive = pd.isnull(df['Invasive'])
		df = df[is_not_invasive]

	# Filter deer
	is_not_browse = df['Palatable Browse Animal'] == 'Low'
	is_some_browse = df['Palatable Browse Animal'] == 'Medium'

	if filter_args['animal_browse'] == 'low-med-high':
		pass
	if filter_args['animal_browse'] == 'low-med':
		df = df[is_not_browse | is_some_browse ]
	if filter_args['animal_browse'] == 'low':
		df = df[is_not_browse ]

	# Filter C:N
	is_cn_low = df['C:N Ratio'] == 'Low'
	is_cn_med = df['C:N Ratio'] == 'Medium'

	if filter_args['cn_ratio'] == 'low-med-high':
		pass
	if filter_args['cn_ratio'] == 'low-med':
		df = df[is_cn_low | is_cn_med ]

	# Filter soil
	is_fine = df['Adapted to Fine Textured Soils'] == 'Yes'
	is_medium = df['Adapted to Medium Textured Soils'] == 'Yes'
	is_course = df['Adapted to Coarse Textured Soils'] == 'Yes'
	is_not_marsh = df['Moisture Use'] != 'High'

	df = df[is_not_marsh]

	if filter_args['soil_texture'] == 'fine':
		df = df[is_fine ]
	if filter_args['soil_texture'] == 'med-fine':
		df = df[is_medium | is_fine]
	if filter_args['soil_texture'] == 'med':
		df = df[is_medium ]
	if filter_args['soil_texture'] == 'med-course':
		df = df[is_medium | is_course]
	if filter_args['soil_texture'] == 'course':
		df = df[is_course]


	# Filter hardiness
	is_above = df['Temperature, Minimum (°F)'] <= int(filter_args['hardiness'])
	df = df[is_above]


	# Filter light
	if filter_args['full_shade']:
		is_sun = df['Shade Tolerance'] == "Tolerant"
	elif filter_args['full_sun']:
		is_sun = df['Shade Tolerance'] == "Intolerant"
	else:
		is_sun = df['Shade Tolerance'] != "Intolerant"
	
	df = df[is_sun]

	# Filter height
	if filter_args['full_sun'] or filter_args['max_height']:
		is_height = pd.notnull(df['Height at Base Age, Maximum (feet)'])
		df = df[is_height]

		if filter_args['max_height']:
			is_max_height = df['Height at Base Age, Maximum (feet)'] <= int(filter_args['max_height'])
		else:
			is_max_height = df['Height at Base Age, Maximum (feet)'] <= 2

		df = df[is_max_height]

	# Filter rainfall

	is_low = df['Precipitation (Minimum)'] <= int(filter_args['percip_min'])
	is_high = df['Precipitation (Maximum)'] >= int(filter_args['percip_max'])

	df = df[is_low & is_high]

	count = len(df)

	return df, count