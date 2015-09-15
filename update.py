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
import csv
#from identity import data_file
#from identity import keys


if __name__ == "__main__":
    '''
This script will read in all objects in the objects folder, determine if they are different from the database object, and post or patch them to the database.
Authentication is determined from the keys.txt file.
'''
    # FUTURE: Should also be deal with errors that are only dependency based.

    # load objects in object folder. MODIFY TO HAVE USER VIEW AND SELECT OBJECTS
    #object_filenames = os.listdir('objects/')
    
    # run for each object in objects folder
    #for object_filename in object_filenames:
        #if '.json' in object_filename:


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
        # define object parameters. NEEDS TO RUN A CHECK TO CONFIRM THESE EXIST FIRST.
        object_type = str(new_object[u'@type'][0])
        # if the accession does not exist, make it blank
	#Padma: remove object_type for biosample_characterization
	if 'biosample_characterization' in new_object[u'@type'] :
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

        # if the id does not exist, assign the uuid. if no uuid, blank.
        #if new_object.has_key(u'@id'):
        #    object_id = str(new_object[u'@id'])
        #else:
        #    None
            #object_id = '' # THIS DOESN"T WORK
        # get relevant schema
        #print('Getting Schema.')
        object_schema = GetENCODE(('/profiles/' + object_type + '.json'),keys)

        # check to see if object already exists
        # PROBLEM: SHOULD CHECK UUID AND NOT USE ANY SHORTCUT METADATA THAT MIGHT NEED TO CHANGE
        # BUT CAN'T USE UUID IF NEW... HENCE PROBLEM
        #print('Checking Object.')
        if object_id != '':
            old_object = GetENCODE(object_id,keys)


# # test the validity of new object
# if not ValidJSON(object_type,object_id,new_object):
# # get relevant schema
# object_schema = get_ENCODE(('/profiles/' + object_type + '.json'))
#
# # test the new object. SHOULD HANDLE ERRORS GRACEFULLY
# try:
# jsonschema.validate(new_object,object_schema)
# # did not validate
# except Exception as e:
# print('Validation of ' + object_id + ' failed.')
# print(e)
#
# # did validate
# else:
# # inform the user of the success
# print('Validation of ' + object_id + ' succeeded.')
#
# # post the new object(s). SHOULD HANDLE ERRORS GRACEFULLY
# response = new_ENCODE(object_collection,new_object)

        # if object is not found, verify and post it
        if (old_object.get(u'title') == u'Not Found') | (old_object.get(u'title') == u'Home'):

            # clean object of unpatchable or nonexistent properties. SHOULD INFORM USER OF ANYTHING THAT DOESN"T GET POSTED.
           # new_object = CleanJSON(new_object,object_schema,'POST')
    
            new_object = FlatJSON(new_object,keys)
            # print(new_object)
            # test the new object
            if ValidJSON(object_type,object_id,new_object,keys):
            	# post the new object(s). SHOULD HANDLE ERRORS GRACEFULLY
                new_object = CleanJSON(new_object,object_schema,'POST')
                response = new_ENCODE(object_type,new_object,keys)
		#print response['status']
		if response['status'] == 'success':
			object_check = GetENCODE(str(response[u'@graph'][0][u'@id']),keys)
	        #	print object_check
		#	print(object_check[u'@id'], object_check[u'uuid'])
			posted_objects.append(object_check)
		if response['status'] == 'error':
			new_object.update({'description':response['description']})
			new_object.update({'errors':response['errors']})
			new_object.update({'object_type':object_type})
			error_objects.append(new_object)

######################

        # if object is found, check for differences and patch it if needed/valid.
        elif put_status:
            # clean object of unpatchable or nonexistent properties. SHOULD INFORM USER OF ANYTHING THAT DOESN"T GET PUT.
            new_object = CleanJSON(new_object,object_schema,'POST')
            new_object = FlatJSON(new_object,keys)
            print('Running a put.')
            print(new_object)
            response = replace_ENCODE(object_id,new_object,keys)
        else:
            # clean object of unpatchable or nonexistent properties. SHOULD INFORM USER OF ANYTHING THAT DOESN"T GET PATCHED.
            new_object = CleanJSON(new_object,object_schema,'PATCH')
            new_object = FlatJSON(new_object,keys)
            # flatten original (to match new)
            old_object = FlatJSON(old_object,keys)
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
                    #print(patch_single)
                    response = patch_ENCODE(object_id,patch_single,keys)
                patched_objects.append(new_object)
            else:
                print('\n\n' + object_id + ' has no updates.')
    # write object to file
    print '\n\n'    

    print 'Patched ' + str(len(patched_objects))+ ' items'
    
    # file to print uuid's to
    filename = 'uploaded_objects.txt'
    print 'Writing '+ str(len(posted_objects))+ ' items to UPLOADED file: '+ filename
  

    errfilename = 'uploaded_error_objects.txt'
    print 'Writing '+ str(len(error_objects))+ ' objects to ERROR file: '+ errfilename
    WriteJSON(error_objects,errfilename)
