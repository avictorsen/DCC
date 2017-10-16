# source code obtained from https://github.com/ENCODE-DCC/WranglerScripts
# ENCODE Tools functions
from ENCODETools import get_ENCODE
from ENCODETools import patch_ENCODE
from ENCODETools import replace_ENCODE
from ENCODETools import new_ENCODE
from ENCODETools import GetENCODE
#from ENCODETools import KeyENCODE
from ENCODETools import ReadJSON
#from ENCODETools import WriteJSON
from ENCODETools import ValidJSON
from ENCODETools import CleanJSON
from ENCODETools import FlatJSON
#from ENCODETools import EmbedJSON
from ENCODETools import WriteJSON
import sys
import csv
import pickle
import collections

if __name__ == "__main__":
    '''
This script will read in all objects in the objects folder, determine if they are different from the database object, and post or patch them to the database.
Authentication is determined from the keys.txt file.
'''
    filename = open('uploaded_objects.txt','w')
    key_open = open('../keys.txt')
    key_file = csv.DictReader(key_open,delimiter = '\t')
    for key in key_file:
        if key.get('server') == 'DCC':
           encoded_access_key = key.get('user')
           encoded_secret_access_key = key.get('password')
        elif key.get('server') == 'GOOGLE':
           client_email = key.get('user')
           PW_file = key.get('password')
        else:
           print
    keys = {'server':'https://www.encodeproject.org/', 'authid':encoded_access_key, 'authpw':encoded_secret_access_key}

    # load object SHOULD HANDLE ERRORS GRACEFULLY
    print('Opening import.json')
    object_list = ReadJSON('import.json')

    # PUT OVERRIDE: SET THIS TO TRUE IF YOU WANT TO PUT INSTEAD OF PATCH
    put_status = False

    counter_post_success = 0
    counter_post_fail = 0
    counter_patch_success = 0
    counter_patch_fail = 0

#################################
#list of uploaded objects
#################################
    posted_objects = []
    error_objects = []
    patched_objects = []
    for new_object in object_list:
        #print new_object
        # define object parameters. NEEDS TO RUN A CHECK TO CONFIRM THESE EXIST FIRST.
        object_type = str(new_object[u'@type'][0])
        # if the accession does not exist, make it blank
	if 'biosample_characterization' in new_object[u'@type']:
	    del new_object[u'@type']
        object_id = ''
        if new_object.has_key(u'accession'):
            object_name = str(new_object[u'accession'])
        else:
            object_name = ''
        if new_object.has_key(u'aliases'):
            object_alias = new_object[u'aliases'][0]
            object_id = str(object_alias)
        else:
            object_alias = ''
        if new_object.has_key(u'uuid'):
            object_uuid = str(new_object[u'uuid'])
            object_id = str(object_uuid)
        else:
            object_uuid = ''
#        if new_object.has_key(u'organism'):
#            ordered_object = collections.OrderedDict({'organism': new_object[u'organism']})
#            ordered_object.update(new_object)
#            new_object = ordered_object
#            print new_object
            #sys.exit()

        #print('Getting Schema.')
        object_schema = GetENCODE(('/profiles/' + object_type + '.json'),keys)
        # check to see if object already exists
        #print('Checking Object.')
        if object_id != '':
            old_object = GetENCODE(object_id,keys)
        # if object is not found, verify and post it
        if (old_object.get(u'title') == u'Not Found') | (old_object.get(u'title') == u'Home'):
            #new_object = FlatJSON(new_object,keys)
            print '\n\nalias:',new_object[u'aliases'][0],'is new.'
            # test the new object
            if ValidJSON(object_schema,object_type,object_id,new_object,keys):
            	# post the new object(s). SHOULD HANDLE ERRORS GRACEFULLY
                new_object = CleanJSON(new_object,object_schema,'POST')
                response = new_ENCODE(object_type,new_object,keys)
		#print response['status']
		if response['status'] == 'success':
			object_check = GetENCODE(str(response[u'@graph'][0][u'@id']),keys)
	         #	print object_check
			print 'uuid:', object_check[u'uuid']
                        filename.write(str(new_object['aliases'][0])+'\t'+str(object_check['uuid'])+'\n')
			posted_objects.append(object_check)
                elif response['status'] == 'error':
                        #print response
			new_object.update({'description':response['description']})
			new_object.update({'errors':response['error']})
			new_object.update({'object_type':object_type})
			error_objects.append(new_object)
                else:
                    sys.exit()
        # if object is found, check for differences and patch it if needed/valid.
        elif put_status:
            # clean object of unpatchable or nonexistent properties. SHOULD INFORM USER OF ANYTHING THAT DOESN"T GET PUT.
            new_object = CleanJSON(new_object,object_schema,'POST')
            #new_object = FlatJSON(new_object,keys)
            print('Running a put.')
            response = replace_ENCODE(object_id,new_object,keys)
        else:
            # clean object of unpatchable or nonexistent properties. SHOULD INFORM USER OF ANYTHING THAT DOESN"T GET PATCHED.
            new_object = CleanJSON(new_object,object_schema,'PATCH')
            #new_object = FlatJSON(new_object,keys)
            #print new_object
            # flatten original (to match new)
            #old_object = FlatJSON(old_object,keys)
            # compare new object to old one, remove identical fields.
            for key in new_object.keys():
                if new_object.get(key) == old_object.get(key):
                    new_object.pop(key)
            # if there are any different fields, patch them. SHOULD ALLOW FOR USER TO VIEW/APPROVE DIFFERENCES
            if new_object:
                # inform user of the updates
                print('\n\n' + object_id + ' has updates.')
                # patch each field to object individually
                for key,value in new_object.items():
                    patch_single = {}
                    patch_single[key] = value
                    #print value
                    response = patch_ENCODE(object_id,patch_single,keys)
                patched_objects.append(new_object)
            else:
                print('\n\n' + object_id + ' has no updates.')
    print '\n'    
    print 'Patched ' + str(len(patched_objects))+ ' items'
    print 'Writing '+ str(len(posted_objects))+ ' items to UPLOADED file: uploaded_objects.txt'
    errfilename = 'uploaded_error_objects.txt'
    print 'Writing '+ str(len(error_objects))+ ' objects to ERROR file: '+ str(errfilename)
    WriteJSON(error_objects,errfilename)
