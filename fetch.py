import requests
import json
import csv
import sys
import re

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
                    if sys.argv[2]:
                        for i in response.json()[query]:
                           print line ,
                           if type(i) is dict:
                               for pip in sys.argv[2].split(","):
                                   print i[pip] ,
                           elif type(i) is unicode:
                               if re.match(".*ENC.*", i):
                                   try:
                                       nextresponse = requests.get(host+i,auth=(encoded_access_key, encoded_secret_access_key),headers={'content-type': 'application/json'})
                                   except:
                                       print nextresponse ,
                                   for pip in sys.argv[2].split(","):
                                       if pip in nextresponse.json():
                                           print nextresponse.json()[pip] ,
                                       else:
                                           print "no_match_for_"+pip ,
                               else:
                                   print i ,
                           print ""
                        print ""
                    else:
                        print "else" + line ,
                        for i in response.json()[query]:
                           print i,
                        print ""
                elif type(response.json()[query]) is dict:
                    for pip in sys.argv[2].split(","):
                        if pip in response.json():
                            print response.json()[query][pip] ,
                        else:
                            print "no_match_for_"+pip ,
                    print ""
                else:
                    print response.json()[query]
                    #print "unknown_object_type_for_" + line
            else:
                print "couldn't_find_" + query +"_for_" + line
            #sys.exit()
main()
