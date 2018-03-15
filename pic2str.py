import re
import base64
import sys
import hashlib
import os
import image
from email.MIMEBase import MIMEBase
from email import Encoders
from PIL import Image
dim = 0
width = 0
height = 0

#file = raw_input("what file?")
#pic2str(file)

def pic2str(file):
    dim = ''
    width = ''
    height = ''
    #pull file name
    name = os.path.basename(file)
    #print name
    temp = re.search('(\w+)$', file)
    if temp.group() == 'tif':
        format = 'image/tiff'
        with open(file) as imageFile:
            mime = base64.b64encode(imageFile.read()).replace('\n','')
        dim = Image.open(file)
        width = str(dim.size[0])
        height = str(dim.size[1])
    elif temp.group() == 'gif':
        format = 'image/' + temp.group()
        with open(file) as imageFile:
            mime = base64.b64encode(imageFile.read()).replace('\n','')
        dim = Image.open(file)
        width = str(dim.size[0])
        height = str(dim.size[1])
    elif (temp.group() == 'jpg') or (temp.group() == 'jpeg'):
        format = 'image/jpeg'
        with open(file) as imageFile:
            mime = base64.b64encode(imageFile.read()).replace('\n','')
        dim = Image.open(file)
        width = str(dim.size[0])
        height = str(dim.size[1])
    elif temp.group() == 'pdf':
        format = 'application/pdf'
        pdf = open(file, 'rb').read()
        attachFile = MIMEBase('application', 'pdf')
        attachFile.set_payload(pdf)
        Encoders.encode_base64(attachFile)
        mime = MIMEBase.get_payload(attachFile).replace('\n','')
    else:
        print 'ERROR! file: ' + file + '\tformat: ' + temp.group()
    md5sum = hashlib.md5()
    with open(file, 'rb') as f:
       for chunk in iter(lambda: f.read(1024*1024), ''):
            md5sum.update(chunk)
    f.close()
    mbsize = os.path.getsize(file)
    #print 'download: ' + name, 'type: ' + format, 'href: data:' + format + ';base64,'# + str
    #print ('{download: ' + name, 'type: ' + format, 'href: data:' + format + ';base64,' + 'MIME'  + '}')
    if temp.group() == 'pdf':
        return ('download: ' + name, 'size: ' + str(mbsize), 'md5sum: ' + md5sum.hexdigest(), 'type: ' + format, 'href: data:' + format + ';base64,' + mime)
    else:
        return ('download: ' + name, 'size: ' + str(mbsize), 'width: ' + str(width), 'height: ' + str(height), 'md5sum: ' + md5sum.hexdigest(), 'type: ' + format, 'href: data:' + format + ';base64,' + mime)


