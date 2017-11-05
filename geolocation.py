import pandas as pd
from geopy.geocoders import Nominatim
import re

geolocator = Nominatim()

members = pd.read_excel('member_data.xlsx')

def gps_coordinates(data):
    try:
        location = geolocator.geocode(data['full_address'])
        if location != None:
            data['latitude'] = location.latitude
            data['longitude'] = location.longitude
    except Exception:
        pass

    return data

members['full_address'] = members['address_line'] + ' , ' + members['city'] + ' , ' + members['state']
for index, row in members.iterrows():
    if re.search(r'\d+\s*\-\s*\d+', row['full_address']):
        row['full_address'] = re.split(r'\d+\s*\-',row['full_address'])[-1]

    # print(index)
    # location = geolocator.geocode(row['full_address'])
    # print(location.address)



members = members.apply(gps_coordinates, axis=1)

writer = pd.ExcelWriter('members_new.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
members.to_excel(writer, sheet_name='Sheet1', index = False)
