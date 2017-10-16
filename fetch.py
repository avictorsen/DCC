import requests
import json
import csv
import sys

def main():
    query = sys.argv[1]
    host = 'https://www.encodeproject.org/'
    key_open = open('../keys.txt')
    keys = csv.DictReader(key_open,delimiter = '\t')
    for key in keys:
        if key.get('server') == 'DCC':
            encoded_access_key = key.get('user')
            encoded_secret_access_key = key.get('password')
        else:
            print
    with open('./fetch.txt') as input:
        for line in input:
            if not line: continue
            line = line.rstrip()
            try:
                response = requests.get(host+line,auth=(encoded_access_key, encoded_secret_access_key),headers={'content-type': 'application/json'})
                #print response.json()
            except:
                print "couldn't_find_" + line
            if query in response.json():
                #print type(response.json()[query])
                if type(response.json()[query]) is unicode:
                    print line + " " + response.json()[query]
                elif type(response.json()[query]) is list:
                    print line,
                    for i in response.json()[query]:
                       print i,
                    print ""
                else:
                    print response.json()[query]
                    #print "unknown_object_type_for_" + line
            else:
                print "couldn't_find_" + query +"_for_" + line

main()
