from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import pandas as pd

df = pd.read_csv('12072016_plants.csv', encoding="utf-8")

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

	seeds_perLb = sub_soup.find_all("div", {"class": "info_block"})[6].contents[2].strip().replace(',','')
	seeds_perLb = int(seeds_perLb)

	price_perUnit = sub_soup.find("div", {"class": "box"}).contents[1].contents[3].contents[2].strip().replace("$","")
	units = sub_soup.find("div", {"class": "box"}).contents[1].contents[3].contents[1].contents[0].split()

	if units[1] == 'lb':
		price_perLb = float(price_perUnit) / int(units[0])
	else:
		print("Error: " + sci_name + "units are " [units[1]])

	result = [sci_name, seeds_perLb, price_perLb]
	sheffields_aval.append(result)


df['Sheffields Aval'] = False
df['Seeds Per Pound'] = False
df['Price Per Pound'] = False

for plant in sheffields_aval:
	for index, row in df.iterrows():
		temp_name = row['Scientific Name']
		temp_name = temp_name.lower()

		if temp_name == plant[0]:
			df['Sheffields Aval'][index] = True
			df['Seeds Per Pound'][index] = plant[1]
			df['Price Per Pound'][index] = plant[2]

import pdb; pdb.set_trace()

df.to_csv('12072016_plants_sheff.csv', sep=',', encoding='utf-8')

