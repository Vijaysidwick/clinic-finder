from flask import Flask, request, redirect
from algoliasearch import algoliasearch
import json
import re
import os
import geocoder

app = Flask(__name__)
client = algoliasearch.Client("user", 'passs')
index = client.init_index('temp')

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    if request.method == 'POST':
        text = request.data.decode('utf-8').replace(u'\ufeff', '')
        print(str(text))
        g = geocoder.arcgis(str(text))
        geoco = g.geojson
        lat = geoco['features'][0]['geometry']['coordinates'][1]
        lon = geoco['features'][0]['geometry']['coordinates'][0]
        aroundLatLng = str(lat)+','+str(lon)
        print(aroundLatLng)
        result = index.search('', {"aroundLatLng": aroundLatLng})
        msg_result = "Nearest clinic for your location is : \n"
        #msg_result += "Serial Number : "+str(result['hits'][0]['Serial Number'])+"\n"
        msg_result += "Name : "+str(result['hits'][0]['Name'])+"\n"
        msg_result += "Address-1 : "+str(result['hits'][0]['Address-1'])+"\n"
        msg_result += "Address-2 : "+str(result['hits'][0]['Address-2'])+"\n"
        msg_result += "City : "+str(result['hits'][0]['City'])+"\n"
        msg_result += "State : "+str(result['hits'][0]['State'])+"\n"
        msg_result += "Zip Code : "+str(result['hits'][0]['Zip'])+"\n"
        msg_result += "Phone Number : "+str(result['hits'][0]['Phone Number'])+"\n"
        msg_result += "Website : "+str(result['hits'][0]['Website'])+"\n"
        print(msg_result)
        return str(msg_result)
    else:
        return "Hello Welcome to Clinic-finder"
               
if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
