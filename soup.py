from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

df = pd.read_csv('plants-deer-full-commercial.csv', encoding="utf-8")

url= 'https://sheffields.com/admin/inventory_raport_manage/pdf_list_page/0/0/2500/0'
page = urlopen(url)
soup = BeautifulSoup(page.read(), "html")

name = soup.find_all("td", {"class": "marin_td name_td"})

sheffields_aval = []

for tag in name:
	sci_name = tag.text.split()[:2]
	sci_name = ' '.join(sci_name)
	sci_name = sci_name.lower()
	sheffields_aval.append(sci_name)

df['Sheffields Aval'] = False

for name in sheffields_aval:
	for index, row in df.iterrows():
		temp_name = row['Scientific Name']
		temp_name = temp_name.lower()

		if temp_name == name:
			df['Sheffields Aval'][index] = True

df.to_csv('full_deer_sheffields.csv', sep=',', encoding='utf-8')

