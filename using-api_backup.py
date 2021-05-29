from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import requests
import json
import xmltodict
import re
import os
import time
import sys

app = Flask(__name__)

Host = "hostname"
Database = "dbname"
User = "user"
Port = 1234
Password = 'password'
URI = "postgres://user:pass@host:port/dbname"

conn = psycopg2.connect("host='host' port='port' dbname='dbname' user='user' password='password'")
cur = conn.cursor()

google_api_url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins=95928&destinations=95928&key=ABC"
geonames_api_url = "http://api.geonames.org/findNearbyPostalCodes?postalcode=95928&country=US&username=xyz"
available_pincodes = ['95928', '72211', '85018', '85021', '92707', '90211', '94143-1648', '94158', '94115', '94143', '94118', '94107', '94132', '94118', '94015', '95928', '96002', '95945', '80304', '80301', '80501', '6106', '6606', '32216', '33761', '33901', '32609', '32216', '33813', '33613', '32810', '34239', '33609', '33713', '32701', '33321', '32601', '33407', '30342', '30309', '30329', '30324', '52245', '60191', '60640', '62040', '61614', '60646', '46222', '67218', '40202', '1915', '1915', '1830', '1843', '20814', '20812', '21236', '4401', '04332-0587', '48075', '48310', '48185', '48219', '48235', '48504', '48603', '55802', '55404', '39216', '59937', '59802', '8034', '680053', '28211', '27406', '27607', '28273', '3301', '3840', '13851', '10605', '10023', '11415', '14214', '11435', '10455', '10017', '58102', '44120', '73109', '19013', '19106', '15206', '18017', '19104', '38104', '76116', '78753', '78222', '78501', '77004', '22901', '22046', '98101', '98115', '98057', '98103', '98405', '53202']
welcome = ['hi','hai','hello','helo','hello hi','hey','hey there','greetings','heya','hello there','hello again','get started']


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    start = time.time()
    body = request.values.get('Body', None)
    resp = MessagingResponse()
    body = body.replace('\ufeff', '').lower()
    if body.lower() in welcome:
        resp.message("Welcome to CLINIC FINDER. I can help you find the nearest clinic. What's your zip code?")
    elif hasNumbers(body):
        pincode = re.search(r'(\d{5}$)|(\d{5}-\d{4}$)',body)
        pincode = pincode.group(0)
        if pincode in available_pincodes:
            print("Matched")
            cur.execute("select * from clinic where zip='"+str(pincode)+"'")
            address = cur.fetchall()
            resp.message("Name : "+str(address[0][1])+",\nAddress-1 : "+str(address[0][2])+",\nAddress-2 : "+str(address[0][3])+",\nCity : "+str(address[0][4])+"\nState : "+str(address[0][5])+",\nZip:"+str(address[0][6])+",\nPhone Number :"+str(address[0][7])+",\nWebsite :"+str(address[0][8])+"")
        else:
            xml_resp  = requests.get("http://api.geonames.org/findNearbyPostalCodes?postalcode="+str(pincode)+"&country=US&radius=30&username=vijay_m")
            json_resp = json.loads(json.dumps(xmltodict.parse(xml_resp.text)))['geonames']
            if 'code' in json_resp: 
                code = json_resp['code']
                nearby_list = []
                for each_code in code:
                    if each_code['postalcode'] in available_pincodes:
                        print("Matched "+str(each_code['postalcode']))
                        cur.execute("select *  from clinic where zip = '"+str(each_code['postalcode'])+"'")
                        response = cur.fetchall()
                        resp.message("Name : "+str(response[0][1])+",\nAddress-1 : "+str(response[0][2])+",\nAddress-2 : "+str(response[0][3])+",\nCity : "+str(response[0][4])+"\nState : "+str(response[0][5])+",\nZip:"+str(response[0][6])+",\nPhone Number :"+str(response[0][7])+",\nWebsite :"+str(response[0][8])+"")
                        return str(resp)
                    else:
                        nearby_list.extend([each_code['postalcode']])
                a = second_set(start,nearby_list[1:])
                resp.message("Name : "+str(a[0][1])+",\nAddress-1 : "+str(a[0][2])+",\nAddress-2 : "+str(a[0][3])+",\nCity : "+str(a[0][4])+"\nState : "+str(a[0][5])+",\nZip:"+str(a[0][6])+",\nPhone Number :"+str(a[0][7])+",\nWebsite :"+str(a[0][8])+"")
                return str(resp)
            else:
                resp.message("Not a Valid Postal Code. Please Try again")
    else:
        resp.message("Sorry, I dint get that. Please send me your Zip code.")
    return str(resp)

def second_set(start,nearby_list):
    recursive_pincode = []
    response = []
    for each_nearby in nearby_list:
        xml_resp  = requests.get("http://api.geonames.org/findNearbyPostalCodes?postalcode="+str(each_nearby)+"&country=US&radius=30&username=username")
        json_resp = json.loads(json.dumps(xmltodict.parse(xml_resp.text)))
        code = json_resp['geonames']['code']
        for each_code in code:
            if each_code['postalcode'] in available_pincodes:
                print("Matched "+str(each_code['postalcode']))
                cur.execute("select *  from clinic where zip = '"+str(each_code['postalcode'])+"'")
                response = cur.fetchall()
                return response
            elif each_code['postalcode'] not in nearby_list:
                recursive_pincode.extend([each_code['postalcode']])

    print(str(tuple(set(recursive_pincode))))
    if not response:
        if time.time() - start > 20:
            sys.exit()
        return second_set(start, list(set(recursive_pincode)))
        
               
if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
