import pandas as pd
import numpy as np

# Load soil data

def filter_data():
	df = pd.read_csv('full_deer_sheffields.csv', encoding="utf-8")

	# 21B—Coloma-Tatches complex, 0 to 6 percent slopes 

	# Mean annual precipitation: 28 to 38 inches
	# Frost-free period: 113 to 185 days 

	# Soil
	    # A - 0 to 4 inches: sandy loam			Medium
	    # Bw1 - 4 to 9 inches: sandy loam		Medium
	    # Bw2 - 9 to 15 inches: sandy loam		Medium
	    # Bw3 - 15 to 23 inches: sand			Course
	    # E - 23 to 31 inches: sand 			Course
	    # E and Bt1 - 31 to 43 inches: sand 	Course
	    # E and Bt2 - 43 to 80 inches: sand 	Course

	# Hardiness 5b								-10.0
	# ------------------------------------------------

	# Filter seed
	is_shef = df['Sheffields Aval'] == True
	# is_aval = df['Commercial Availability'] == "Routinely Available"
	df = df[is_shef]

	# Filter nan
	is_not_nan = pd.notnull(df['Growth Rate'])
	df = df[is_not_nan]

	is_not_nan = pd.notnull(df['Height at Base Age, Maximum (feet)'])
	df = df[is_not_nan]

	# Filter invasive
	is_not_invasive = pd.isnull(df['Invasive'])
	df = df[is_not_invasive]

	# Filter deer
	is_not_browse = df['Palatable Browse Animal'] == 'Low'
	is_some_browse = df['Palatable Browse Animal'] == 'Medium'
	is_browse = df['Palatable Browse Animal'] == 'High'
	df = df[is_not_browse | is_some_browse ]

	# Filter C:N
	is_cn_low = df['C:N Ratio'] == 'Low'
	is_cn_med = df['C:N Ratio'] == 'Medium'
	is_cn_high = df['C:N Ratio'] == 'High'

	df = df[is_cn_low | is_cn_med | is_cn_high]

	# Filter soil
	is_medium = df['Adapted to Medium Textured Soils'] == 'Yes'
	is_course = df['Adapted to Coarse Textured Soils'] == 'Yes'
	is_not_marsh = df['Moisture Use'] != 'High'

	df = df[is_course | is_medium | is_not_marsh]

	# Filter hardiness

	is_above = df['Temperature, Minimum (°F)'] <= -10.0

	df = df[is_above]

	# Filter light
	is_tol = df['Shade Tolerance'] != "Intolerant"

	df = df[is_tol]

	# Filter rainfall

	is_low = df['Precipitation (Minimum)'] >= 28
	is_high = df['Precipitation (Maximum)'] >= 38

	df = df[is_low & is_high]
	count = len(df)

	return df, count

def calc_pop(area, height):

	result = area/height

	return result