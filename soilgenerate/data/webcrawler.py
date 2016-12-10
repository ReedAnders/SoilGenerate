from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
import pandas as pd

# Sheffields Seed data collector
# TODO: Clean up

df = pd.read_csv('12072016_plants.csv', encoding="utf-8")

comparison_dict = {}

def compare(comp_dict, result):
	goahead = False
	entry = comp_dict.get(result[0])

	if entry:
		previous = entry[1]/entry[0]
		current = result[2]/result[1]
		if current < previous:
			goahead = True
	elif not entry:
		goahead = True
	
	return goahead

# Clean up df
is_not_nan = pd.notnull(df['Growth Rate'])
df = df[is_not_nan]

is_not_nan = pd.notnull(df['Planting Density per Acre, Maximum'])
df = df[is_not_nan]

url= 'https://sheffields.com/admin/inventory_raport_manage/pdf_list_page/0/0/2500/0'
page = urlopen(url)
soup = BeautifulSoup(page.read(), "html")

name = soup.find_all("td", {"class": "marin_td name_td"})

sheffields_aval = []

for tag in name:
	sci_name = tag.text.split()[:2]
	sci_name = ' '.join(sci_name)
	sci_name = sci_name.lower()

	href = tag.find("a", href=True)['href']
	
	r = requests.get(href, allow_redirects=False)
	sub_page = r.content
	sub_soup = BeautifulSoup(sub_page)

	label_dict = {}
	label_list = sub_soup.find_all("div", {"class": "info_block"})

	try:
		for item in label_list:
			key = item.contents[1].text[:-1]
			value = item.contents[2]
			value = re.sub("[^\d.]+", "", value)
			label_dict[key] = value
	except Exception as e:
		continue

	seeds_perLb = label_dict.get('Seeds Per Pound')

	if seeds_perLb:
		seeds_perLb = float(seeds_perLb)
	else:
		continue


	price_dict = {}
	try:
		tree_list = sub_soup.find("div", {"class": "box"}).contents[1].contents
	except Exception as e:
		continue

	for item in tree_list:
		if item != "\n":
			unit = item.contents[1].contents[0].split()
			
			price = item.contents[2]
			price = re.sub("[^\d.]+", "", price)

			try:
				price_dict[unit[1]] = float(price) / float(unit[0])
			except Exception as e:
				print(price, unit[0])


	lb = price_dict.get('lb')
	oz = price_dict.get('oz')
	g = price_dict.get('g')
	kg = price_dict.get('kg')

	if lb:
		result = [sci_name, seeds_perLb, lb]
		if compare(comparison_dict, result):
			comparison_dict[sci_name] = (seeds_perLb, result[2])
			sheffields_aval.append(result)
			print(result, result[2]/result[1])
	elif oz:
		result = [sci_name, seeds_perLb, oz*16]
		if compare(comparison_dict, result):
			comparison_dict[sci_name] = (seeds_perLb, result[2])
			sheffields_aval.append(result)
			print(result, result[2]/result[1])
	elif g:
		result = [sci_name, seeds_perLb, g*453.592]
		if compare(comparison_dict, result):
			comparison_dict[sci_name] = (seeds_perLb, result[2])
			sheffields_aval.append(result)
			print(result, result[2]/result[1])
	elif kg:
		result = [sci_name, seeds_perLb, kg*0.453592]
		if compare(comparison_dict, result):
			comparison_dict[sci_name] = (seeds_perLb, result[2])
			sheffields_aval.append(result)
			print(result, result[2]/result[1])
	else:
		print("Error: ")
		result = False
		print(sci_name)
		print(price_dict, seeds_perLb)


df['Sheffields Aval'] = False
df['Seeds Per Pound'] = 99999.9
df['Price Per Pound'] = 99999.9

for plant in sheffields_aval:
	for index, row in df.iterrows():
		temp_name = row['Scientific Name']
		temp_name = temp_name.lower()

		if temp_name == plant[0]:
			df['Sheffields Aval'][index] = True
			df['Seeds Per Pound'][index] = plant[1]
			df['Price Per Pound'][index] = plant[2]

df.to_csv('12072016_plants_sheff.csv', sep=',', encoding='utf-8')

