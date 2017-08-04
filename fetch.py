import requests
import json
import csv
import sys

def main():
    query = sys.argv[2]
    print query
    host = 'https://www.encodeproject.org/'
    key_open = open('../keys.txt', 'r')
    keys = csv.DictReader(key_open,delimiter = '\t')
    for key in keys:
        if key.get('server') == 'DCC':
            encoded_access_key = key.get('user')
            encoded_secret_access_key = key.get('password')
        else:
            print
            
    input = open('./fetch.txt')        
    foreach pip in input:
        try:
            response = requests.get(host+'pip',auth=(encoded_access_key, encoded_secret_access_key),headers={'content-type': 'application/json'})
            #print response
        except errors:
            print "couldn't_find_" + pip
            
    
main()
