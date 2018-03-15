# source code obtained from https://github.com/ENCODE-DCC/WranglerScripts
from pic2str import pic2str
import sys
import re
import os
import mimetypes
import csv
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import errors, http
from apiclient.discovery import build
import urllib
import xlrd
import hashlib
import json
import requests
import subprocess
import string

key_open = open('../keys.txt')
keys = csv.DictReader(key_open,delimiter = '\t')
for key in keys:
    if key.get('server') == 'DCC':
        encoded_access_key = key.get('user')
        encoded_secret_access_key = key.get('password')
    elif key.get('server') == 'GOOGLE':
        client_email = key.get('user')
        PW_file = key.get('password')
    else:
        print


json_file = 'import.json'
host = 'https://www.encodeproject.org/'
spreadname = sys.argv[1]
workbook = sys.argv[2]

#login credentials
with open(PW_file) as f:
    private_key = f.read()
#flow = client.flow_from_clientsecrets(private_key,'https://www.googleapis.com/auth/drive.readonly')
scope = ['https://www.googleapis.com/auth/drive.readonly']
#scope = ['https://www.googleapis.com/auth/drive.readonly']credentials = ServiceAccountCredentials.from_json_keyfile_name(PW_file, scope)
credentials = ServiceAccountCredentials.from_json_keyfile_name(PW_file, scope)
http_auth = credentials.authorize(Http())
drivelogin = build('drive', 'v3', http=http_auth)


#gets list of googleDOC files
result = []
page_token = None
while True:
    try:
#        param = {'corpora': 'domain', 'q': "title contains '_'"}
#        files = drivelogin.files().list(**param).execute()
#        result.extend(files['items'])
        files = drivelogin.files().list(fields="nextPageToken, files(*)").execute()
        items = files.get('files', [])
        if not items:
            print "no files found"
            sys.exit()
#        page_token = files.get('nextPageToken')
        if not page_token:
           break
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        break
#compare list of files to inputed spreadname
for i in items:
    if i['name'] == spreadname:
        spreadid = i['id']
#        selflink = i['selfLink']
        #print spreadid
try:
    #selflink
    spreadid
except NameError:
    print 'spreadsheet not found'
    sys.exit()
print "Opening spreadsheet: "+ spreadname
file = 'temp_submit_file.xlsx'

#get actual data
#download_url = drivelogin.files().get(fileId=spreadid).execute()['exportLinks']['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
response = drivelogin.files().export(fileId=spreadid,mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
if response:
    with open(file, 'wb') as fh:
        fh.write(response)
#if download_url:
#    response = urllib.urlopen(download_url)
#    if response.getcode() == 200:
#        urllib.urlretrieve(download_url, file)
else:
    print 'Could not download file' + response
    sys.exit()
#open workbook.
try:
    book = xlrd.open_workbook(file)
except errors:
    print 'could not open workbook'
    os.remove(file)
    sys.exit()
try:
    work = book.sheet_by_name(workbook)
except errors:
    print 'could not find workbook'
    os.remove(file)
    sys.exit()
print "Processing worksheet: " + workbook

# get list of compressed header names
headers = work.row_values(0)
print 'headers:'
print headers
object_list = []
#object_schema = GetENCODE(('/profiles/file.json'),keys)
try:
    response = requests.get(host+'profiles/'+workbook+'.json?limit=all',auth=(encoded_access_key, encoded_secret_access_key),headers={'content-type': 'application/json'})
except errors:
    print "couldn't get JSON schema"
    sys.exit()
object_schema = response.json()
#print object_schema
for row in range(1, work.nrows, 1):
    print
    print
    print "----------------------------------------------------------------"
    #break on blank line
    dieif = 0
    for cell in work.row_values(row,0):
        if cell != '':
            dieif = 1
    if dieif < 1:
        break
    new_object = {u'@type':[workbook,u'item']}
    for colindex,header in enumerate(headers):
        if not object_schema[u'properties'].has_key(header):
            print "no match for " + header
        else:
            value = work.cell_value(row, colindex)
            print '{}: \"{}\"'.format(*[header,value])
            if value != '':
                #print  object_schema[u'properties'][header][u'type']
                # need to fix dates before adding them. Google API does not allow disabling of autoform$
                # use regexp to check for dates (MM/DD/YYYY)
                # then format them as we enter them (YYYY-MM-DD)
                format=re.compile("^[dD]ate")
                #if format.match(object_schema[u'properties'][header][u'format']):
                if re.compile("\d{1,2}\/\d{1,2}\/\d{1,4}").search(str(value)):
                    date = value.split('/')
                    value = date[2] + '-' + date[0] + '-' + date[1]
                if object_schema[u'properties'][header][u'type'] == 'string':
                    new_object.update({header:unicode(value)})
                elif object_schema[u'properties'][header][u'type'] == 'integer':
                    new_object.update({header:int(value)})
                elif object_schema[u'properties'][header][u'type'] == 'number':
                    new_object.update({header:float(value)})
                elif object_schema[u'properties'][header][u'type'] == 'float':
                    new_object.update({header:float(value)})
                elif object_schema[u'properties'][header][u'type'] == 'array':
                    value = value.split(', ')
                    if object_schema[u'properties'][header][u'items'][u'type'] == 'string':
                        new_object.update({header:value})
                    elif object_schema[u'properties'][header][u'items'][u'type'] == 'object':
                        sub_object = dict()
                        for prop_value_pair in value:
                            pair = prop_value_pair.split(': ')
                            if pair[0] == 'lane':
                                sub_object[pair[0]] = int(pair[1])
                            else:
                                sub_object[pair[0]] = pair[1]
                        new_object.update({header: [sub_object]})
                            # upload image as attachment object
                elif object_schema[u'properties'][header][u'type'] == 'object':
                    if header == 'attachment':
                        sub_object = {}
                        print 'filename' + str(value)
                        value = pic2str(value)
                        #print sub_object
                    else:
                        value = value.split(', ')
                    sub_object = dict()
                    for prop_value_pair in value:
                        pair = prop_value_pair.split(': ')
                        print pair[0]
                        if pair[0] == 'start' or pair[0] == 'end' or pair[0] == 'size' or pair[0] == 'height' or pair[0] == 'width':
                            sub_object[pair[0]] = int(pair[1])
                        else:
                            sub_object[pair[0]] = pair[1]
                    new_object.update({header: sub_object})
    object_list.append(new_object)

print 'Writing '+ str(len(object_list))+ ' objects to JSON file: '+ json_file
# write object to file
with open(json_file, 'w') as outfile:
    json.dump(object_list, outfile)
    outfile.close
os.remove(file)






