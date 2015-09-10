import re
import base64
import sys

def pic2str(file):
    #print "What file?"
    #file = sys.argv[1] #raw_input()
    #pull file name
    temp = re.search('\w+\.\w+', file)
    name = temp.group()
    temp = re.search('(\w+)$', file)
    if temp == 'jpg' or 'jpeg' or 'gif':
        format = 'image/' + temp.group()
    #if temp == 'pdf'
    #    format = temp.group()
    #print format
    with open(file) as imageFile:
        str = base64.b64encode(imageFile.read()).replace('\n','')
    return ('dowload: ' + name, 'type: ' + format, 'href: data:' + format + ';base64,' + str)
