import pandas as pd
from geopy.geocoders import Nominatim
import googlemaps
import re

geolocator = Nominatim()
gmaps = googlemaps.Client(key='api-key')

members = pd.read_csv('members_new.csv')

def gps_coordinates(data):
    try:
        location = geolocator.geocode(data['full_address'])
        if location != None:
            data['latitude'] = location.latitude
            data['longitude'] = location.longitude
    except Exception:
        pass

    return data

def gps_coordinates_google(data):
    try:
        geocode_result = gmaps.geocode(data['full_address'])
        #location = geolocator.geocode(data['full_address'])

        if geocode_result != None:
            data['latitude'] = geocode_result[0]['geometry']['location']['lat']
            data['longitude'] = geocode_result[0]['geometry']['location']['lng']
            print(data['latitude'])
    except Exception:
        pass

    return data

#members['full_address'] = members['address_line'] + ' , ' + members['city'] + ' , ' + members['state']
def split_function(data):
    if re.search(r'\d+\s*\-\s*\d+', data['full_address']):
        return re.split(r'\d+\s*\-',data['full_address'])[-1]

    else:
        return data['full_address']

members['full_address'] = members.apply(split_function,axis=1)


members.loc[members['latitude'].isnull()] = members.loc[members['latitude'].isnull()].apply(gps_coordinates, axis=1)

members = members.drop(['full_address'], axis=1)

members.to_csv('members_new.csv')

# writer = pd.ExcelWriter('members_new.xlsx', engine='xlsxwriter')
#
# # Convert the dataframe to an XlsxWriter Excel object.
# members.to_excel(writer, sheet_name='Sheet1', index = False)
