import hashlib
import json
import os
import re
import requests
import subprocess
import time
import sys
import string
#from identity import keys #want to remove
#from ENCODETools import GetENCODE #want to remove
import xlrd
import urllib
from httplib2 import Http
from apiclient import errors, http
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build
import csv

def main():
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

    if (len(sys.argv) < 4):
        print "Error! use arguments: genome; Gdoc_name sheet_name"
    os.system("rmdir --ignore-fail-on-non-empty temp")
    os.system("mkdir temp")
    OUTPUT = open('submit_file_output.txt', 'w')
    host = 'https://www.encodeproject.org/'
    #host = 'https://test.encodedcc.org/'
    #host = 'https://v33b1.demo.encodedcc.org/'
    #Static variables
    #if modENCODE
    
    #if modERN
    my_award = 'U41HG007355'
    
    assay_term_name = 'ChIP-seq'
    assay_term_id = 'OBI:0000716'
    my_lab = 'kevin-white'
    request_type = sys.argv[1]
    spreadname = sys.argv[2]
    workbook = sys.argv[3]

    #login credentials
    with open(PW_file) as f:
        private_key = f.read()
    scope = ['https://www.googleapis.com/auth/drive.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(PW_file, scope)
    http_auth = credentials.authorize(Http())
    drivelogin = build('drive', 'v3', http=http_auth)
    #gets list of googleDOC files
    result = []
    page_token = None
    while True:
        try:
            #corpus:DOMAIN not working as param
            files = drivelogin.files().list(fields="nextPageToken, files(*)").execute()
            items = files.get('files', [])
            if not items:
                print "no files found"
                sys.exit()
            #break loop 
            if not page_token:
                break
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break
    #compare list of files to inputed spreadname
    for i in result:
        if i['name'] == spreadname:
            spreadid = i['id']
            selflink = i['selfLink']
            #print spreadid
    print "Opening spreadsheet: "+ spreadname
    try:
        selflink
    except NameError:
        print 'spreadsheet not found'
        sys.exit()

    file = 'temp_submit_file.xlsx'

    #get actual data
    download_url = drivelogin.files().get(fileId=spreadid).execute()['exportLinks']['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    if download_url:
        response = urllib.urlopen(download_url)
        if response.getcode() == 200:
            urllib.urlretrieve(download_url, file)
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
    #need schema for:
    #IdrSummaryQualityMetric maybe
    #ComplexityXcorrQualityMetric maybe
    #ChipSeqFilterQualityMetric for pbc files
    #SamtoolsFlagstatsQualityMetric for sam files
    for row in range(1, work.nrows, 1):
        print
        print
        print "----------------------------------------------------------------"
        #break on blank line
        dieif = 0
        for cell in work.row_values(row,0):
            if cell is "":
               None
            else:
               dieif = 1
        if dieif == 0:
            break
        #look at switching to just makeing dictionary from row.
        for colindex,header in enumerate(headers):
            print header+':',value
            if len(str(value)) > 0 :
                if header == "quality_metric_of":
                    derived_from = work.cell_value(row, colindex)
                if header == "aliases":
                    aliases = work.cell_value(row, colindex)
                if header == "path_to_file":
                    path = work.cell_value(row, colindex)
                    print header+':', path
                    file = path
                    temp = os.path.splitext(path)
                    if (temp[1] == '.bam'):
                      if time.ctime(os.path.getctime(proggen + ".stats") < (time.time() - 604800):
                        compile()
                      reads = os.popen("grep -A5" + path + " " + progen + ".stats | tail -1 | cut -f2").readlines()
                      if len(reads) < 1:
                            print 'Error: no files found'
                            os.system("rmdir --ignore-fail-on-non-empty temp")
                            sys.exit()
                        if len(file) > 1:
                           print 'More than two sam files found: ',file
                           sys.exit()
                        path = os.path.dirname(file[0].rstrip())
                        stats_file = os.popen("find " + path + " -name *stats").readlines()
                        if len(stats_file)
   
        #compile and send to DCC
        print '\n'+aliases
        DCC(locals(),OUTPUT)
        #if file format is bed, rerun with original bed file
        if (format == 'bed'):
            print "\n\nRepeating submission with bigBed file"
            derived_from = [aliases]
            if rep == '':
                if output_type == "optimal idr threasholded peaks":
                    step = DCC_pooled_pipeline['optimal idr bigBed']
                else:
                    step = DCC_pooled_pipeline['bigBed']
            else:
                step = DCC_rep_pipeline['bigBed']
            aliases = aliases.replace('-bed','-bigBed')
            format = 'bigBed'
            path = path.replace('.gz','.bb')
            print "aliases: "+aliases
            DCC(locals(),OUTPUT)


        ####Clean up
        os.system("rm -f ./temp/*")
    os.system("rmdir --ignore-fail-on-non-empty temp")

def DCC(d, OUTPUT):
    encValData = 'encValData'
    #compile data
    data = {
        "aliases": [d['aliases']],
        "dataset": d['exp'],
        "file_format": d['format'],
        "lab": d['my_lab'],
        "award": d['my_award'],
    }
    ## add specific data to data array
    if ('derived_from' in d['headers']):
        if d['derived_from'] != None:
            data['derived_from'] = d['derived_from']
    if 'type' in d:
        data['file_format_type'] = d['type']
    if 'read_length' in d:
        data['read_length'] = d['read_length']
    if 'run_type' in d:
        data['run_type'] = d['run_type']
    if 'controlled_by' in d:
        data['controlled_by'] = d['controlled_by']
    if 'assembly' in d:
        data['assembly'] = d['assembly']
    if d['output_type'] != None:
        data["output_type"] = d['output_type']
    if 'rep' in d:
        if d['rep'] != None and d['rep'] != '':
            data['replicate'] = d['rep']
    if (d['format'] is 'fastq'):
        data["flowcell_details"] = d['cell']
        data["platform"] = d['platform']
        #to remove paired_end
        if (d['run_type'] == 'paired-ended'):
            data['paired_end'] = d['paired_end']
            if (data['paired_end'] == '2'):
                data['paired_with'] = d['paired_with']
        #data.pop('paired_end')
    if 'step' in d:
        data['step_run'] = d['step']
    
    #print data
    #sys.exit()
    ####################
    # Local validation
    chromInfo = '-chromInfo=%s/%s/chrom.sizes' % (encValData, d['proggen'])
    #if d['proggen'] == 'dm3':
    #    chromInfo += '.nochr'

    validate_map = {
        'bam': ['-type=bam', chromInfo],
        #'bed': ['-type=bed3', chromInfo],
        'bed': ['-type=bed6+', chromInfo],  # if this fails we will drop to bed3+
        'bedLogR': ['-type=bigBed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        'bed_bedLogR': ['-type=bed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        'bedMethyl': ['-type=bigBed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        'bed_bedMethyl': ['-type=bed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        #'bigBed': ['-type=bigBed3', chromInfo],  # if this fails we will drop to bigBed3+
        'bigBed': ['-type=bigBed6+', chromInfo],  # if this fails we will drop to bigBed3+
        'bigWig': ['-type=bigWig', chromInfo],
        'broadPeak': ['-type=bigBed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        'bed_broadPeak': ['-type=bed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        'fasta': ['-type=fasta'],
        'fastq': ['-type=fastq'],
        'gtf': None,
        'idat': ['-type=idat'],
        'narrowPeak': ['-type=bigBed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        'bed_narrowPeak': ['-type=bed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        'rcc': ['-type=rcc'],
        'tar': None,
        'tsv': None,
        '2bit': None,
        'csfasta': ['-type=csfasta'],
        'csqual': ['-type=csqual'],
        'bedRnaElements': ['-type=bed6+3', chromInfo, '-as=%s/as/bedRnaElements.as' % encValData],
        'CEL': None,
    }
    if re.search('regionPeak.gz$',d['path']) != None:
        validate_args = validate_map.get(data['file_format']+"_narrowPeak")
    else:
        validate_args = validate_map.get(data['file_format'])
    if validate_args is not None:
        print"Validating file as " + str(validate_args)
        try:
           subprocess.check_output(['./validateFiles'] + validate_args + [d['path']])
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
    gzip_types = [
        "CEL",
        "bam",
        "bed",
        "bed3",
        "bed6",
        "bed_bed3",
        "bed_bed6",
        "bed_bedLogR",
        "bed_bedMethyl",
        "bed_bedRnaElements",
        "bed_broadPeak",
        "bed_narrowPeak",
        "bed_peptideMapping",
        "csfasta",
        "csqual",
        "fasta",
        "fastq",
        "gff",
        "gtf",
        "tar",
    ]

    magic_number = open(d['path'], 'rb').read(2)
    is_gzipped = magic_number == b'\x1f\x8b'

    print "format:" + d['format']

    #print "gzipped?" + is_gzipped

    if re.search('bed$', data['file_format']) != None:
        test = data['file_format']+"_"+data['file_format_type']
    else:
        test = data['file_format']
    if test in gzip_types:
        if is_gzipped is False:
            gzip = subprocess.Popen(['gzip','-f',d['path']],)
            gzip.wait()
            d['path'] = d['path'] + '.gz'
            if gzip.stderr != None:
                assert is_gzipped, 'Expected gzipped file'
    else:
        #could add step to unzip if needed
        assert not is_gzipped, 'Expected un-gzipped file'

    #calculate md5
    md5sum = hashlib.md5()
    with open(d['path'], 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), ''):
            md5sum.update(chunk)
    print "md5sum: ", md5sum.hexdigest()
    data['md5sum'] = md5sum.hexdigest()
    data['file_size'] = os.path.getsize(d['path'])
    data['submitted_file_name'] = d['path']
    print "submitted_file_name: " + d['path']
    print "file_format: " + data['file_format']
    if 'file_format_type' in data:
        print "file_format_type: "+data['file_format_type']
    if 'step_run' in data:
        print "run_step: " + data['step_run']
    DCCheaders = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }
    if d['request_type'] == 'overwrite':
        data['status'] = 'uploading'
    r = requests.post(
        d['host'] + '/files',
        auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
        data=json.dumps(data),
        headers=DCCheaders,
    )
    print "posting metadata!"
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
        print "r:",r.json()
        print "post failed, trying patch"
        del data['md5sum']
        del data['file_size']
        del data['submitted_file_name']
        s = requests.patch(#change to put to overwrite,patch to ammend
            d['host'] + '/' + d['aliases'],
            auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
            data=json.dumps(data),
            headers=DCCheaders,
        )
        try:
            s.raise_for_status()
        except requests.exceptions.HTTPError:
            print '\ndata: ', data
            print 
            print 'r: ', r.json()
            print 
            print('patch failed: %s %s' % (s.status_code, s.reason))
            print 
            print 's: ', s.json()
            sys.exit()
    if r.json()[u'status'] == 'success':
        print 'uuid: ',r.json()['@graph'][0]['uuid']
        temp = r.json()['@graph'][0]['uuid']
    elif s.json()[u'status'] == 'success':
        print 'uuid: ',s.json()['@graph'][0]['uuid']
        temp = s.json()['@graph'][0]['uuid']

    ##### upload files
    if temp != "" and d['request_type'] == 'patch':
        print "metadata patched!"
    ############### post ###############
    elif temp != "" and d['request_type'] == 'post':
        OUTPUT.write(d['aliases'])
        OUTPUT.write('\t')
        OUTPUT.write(temp)
        OUTPUT.write('\n')
        t = requests.patch(
            d['host'] + '/' + temp,
            auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
            data=json.dumps(data),
            headers=DCCheaders,
        )
        try:
            t.raise_for_status()
        except:
            print "t: ",t.json()
            print "he's dead jim"
            sys.exit();
        #print r.json()
        item = t.json()['@graph'][0]
        #print "r:", r.json()
        #POST file to S3
        creds = item['upload_credentials']
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': creds['access_key'],
            'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
            'AWS_SECURITY_TOKEN': creds['session_token'],
        })
        print("Uploading file.")
        start = time.time()
        
        #this might break due to e.returncode not being defined.
        i = 0
        err_after_4 = True
        while (i < 4):
            try:
                subprocess.check_call(['aws', 's3', 'cp', d['path'], creds['upload_url']], env=env)
                err_after_4 = False
                i = 5
            except subprocess.CalledProcessError as e:
                # The aws command returns a non-zero exit code on error.
                print("Upload failed with exit code %d" % e.returncode)
                print "Retrying"
                time.sleep(2)
                i = i+1
                continue
        if err_after_4 is True:
            print 'upload failed too many times'
            sys.exit()
        end = time.time()
        duration = end - start
        print("Uploaded in %.2f seconds" % duration)
    ############# overwrite ################
    elif temp != "" and d['request_type'] == 'overwrite':
        ID = s.json()['@graph'][0]['accession']
        print "ID: " + ID
        print("Uploading file.")
        temp = s.json()['@graph'][0]['aliases'][0]
        OUTPUT.write(temp)
        OUTPUT.write('\t')
        temp = s.json()['@graph'][0]['uuid']
        OUTPUT.write(temp)
        OUTPUT.write('\n')
        renew_upload_credentials = "curl -X POST -H 'Accept:application/json' -H 'Content-Type:application/json' https://" + d['encoded_access_key'] + ":" + d['encoded_secret_access_key'] + "@www.encodeproject.org/files/" + ID + "/upload -d '{}'"
        t = requests.patch(
            d['host'] + d['aliases'],
            auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
            data=json.dumps(data),
            headers=DCCheaders,
        )
        #print t.json()
        item = json.loads(os.popen(renew_upload_credentials).read())['@graph'][0]
        #item = t.json()['@graph'][0]
        #POST file to S3
        creds = item['upload_credentials']
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': creds['access_key'],
            'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
            'AWS_SECURITY_TOKEN': creds['session_token'],
        })
        print("Uploading file.")
        start = time.time()
        i = 0
        err_after_4 = True
        while (i < 4):
            try:
                subprocess.check_call(['aws', 's3', 'cp', d['path'], creds['upload_url']], env=env)
                err_after_4 = False
                i = 5
            except subprocess.CalledProcessError as e:
                # The aws command returns a non-zero exit code on error.
                print("Upload failed with exit code %d" % e.returncode)
                print "Retrying"
                time.sleep(2)
                i = i+1
                continue
        if err_after_4 is True:
            print 'upload failed too many times'
            sys.exit()
        end = time.time()
        duration = end - start
        print("Uploaded in %.2f seconds" % duration)
    #print s.json()
    else:
        print 'temp failed'
        sys.exit()
    return;

def compile(proggen):
  if proggen == 'dm3' or if proggen == 'dm6'
    os.system("for file in /data/dm/processed/" + proggen + "/2*/*stats; do cat $file >> ~/" + proggen + ".stats")
  if proggen == 'WS220' or if proggen == 'WS245'
    os.system("for file in /data/ce/processed/" + proggen + "/2*/*stats; do cat $file >> ~/" + proggen + ".stats")
  return;
                                    
main()
