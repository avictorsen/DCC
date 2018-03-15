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
from oauth2client.service_account import ServiceAccountCredentials
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
    FAIL = open('submit_file_fail.txt', 'w')
    PATCH = open('submit_file_patched.txt', 'w')
    host = 'https://www.encodeproject.org/'
    #host = 'https://test.encodedcc.org/'
    #host = 'https://v33b1.demo.encodedcc.org/'
    #Static variables
    my_lab = 'kevin-white'
    #modERN
    #my_award = 'U41HG007355'
    #modENCODE
    my_award = 'U01HG004264'
    request_type = sys.argv[1]
    proggen = sys.argv[2]
    spreadname = sys.argv[3]
    workbook = sys.argv[4]
    encValData = 'encValData'

    DCC_rep_pipeline = {
        'alignments': 'modern:chip-seq-bwa-alignment-step-run-v-1-virtual',
        'signal of unique reads': 'modern:chip-seq-unique-read-signal-generation-step-run-v-1-virtual',
        'read-depth normalized signal': 'modern:chip-seq-read-depth-normalized-signal-generation-step-run-v-1-virtual',
        'control normalized signal': 'modern:chip-seq-control-normalized-signal-generation-step-run-v-1-virtual',
        'peaks': 'modern:chip-seq-spp-peak-calling-step-run-v-1-virtual',
        'bigBed': 'modern:chip-seq-peaks-to-bigbed-step-run-v-1-virtual'
        }

    DCC_pooled_pipeline = {
        'signal of unique reads': 'modern:chip-seq-replicate-pooled-unique-read-signal-generation-step-run-v-1-virtual',
        'read-depth normalized signal': 'modern:chip-seq-replicate-pooled-read-depth-normalized-signal-generation-step-run-v-1-virtual',
        'control normalized signal': 'modern:chip-seq-replicate-pooled-control-normalized-signal-generation-step-run-v-1-virtual',
        'peaks': 'modern:chip-seq-spp-peak-calling-step-run-v-1-virtual', #same as replicate
        'bigBed': 'modern:chip-seq-peaks-to-bigbed-step-run-v-1-virtual', #same as replicate
        'optimal idr thresholded peaks': 'modern:chip-seq-optimal-idr-step-run-v-1-virtual',
        'optimal idr bigBed': 'modern:chip-seq-optimal-idr-threasholded-preaks-to-bigbed-step-run-v-1-virtual'
        }
    #login credentials
    with open(PW_file) as f:
        private_key = f.read()
    scope = ['https://www.googleapis.com/auth/drive.readonly']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(PW_file, scope)
    #credentials = SignedJwtAssertionCredentials(client_email, private_key,'https://www.googleapis.com/auth/drive.readonly')
    http_auth = credentials.authorize(Http())
    drivelogin = build('drive', 'v3', http=http_auth)
    #gets list of googleDOC files
    result = []
    page_token = None
    while True:
        try:
            #corpus:DOMAIN not working as param
            files = drivelogin.files().list(fields="nextPageToken, files(*)").execute()
#            files = drivelogin.files().list(**param).execute()
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
    for i in items:
        if i['name'] == spreadname:
            spreadid = i['id']
    print "Opening spreadsheet: "+ spreadname
    try:
        spreadid
    except NameError:
        print 'spreadsheet not found'
        sys.exit()

    file = 'temp_submit_file.xlsx'

    #get actual data
    response = drivelogin.files().export(fileId=spreadid,mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet').execute()
    if response:
        with open(file, 'wb') as fh:
            fh.write(response)
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
        response = requests.get(host+'profiles/file.json?limit=all',auth=(encoded_access_key, encoded_secret_access_key),headers={'content-type': 'application/json'})
        #print response
    except errors:
        print "couldn't get JSON schema"
        sys.exit()
    object_schema = response.json()
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
            #if header == "uuid":
            #    value = work.cell_value(row,colindex)
            #    if value is not '':
            #        new_object.update({header: ''})
            if object_schema[u'properties'].has_key(header):
                value = work.cell_value(row, colindex)
                print header+':',value
                if len(str(value)) > 0 :
                    if header == "file_format_type":
                        type = work.cell_value(row, colindex)
                    if header == "dataset":
                        exp = work.cell_value(row, colindex)
                    if header == "aliases":
                        aliases = work.cell_value(row, colindex)
                    if header == "supersedes":
                        replaces = work.cell_value(row, colindex).split(', ')
                    if header == "replicate":
                        rep = work.cell_value(row,colindex)
                    if header == "derived_from":
                        derived_from = work.cell_value(row, colindex)
                        if derived_from != None:
                            derived_from = derived_from.split(', ')
                    if header == "controlled_by":
                        controlled_by = work.cell_value(row, colindex).split(', ')
                    if header == "assembly":
                        assembly =  work.cell_value(row, colindex)
                    if header == "read_length":
                        read_length = int(work.cell_value(row, colindex))
                    if header == "run_type":
                        run_type = work.cell_value(row, colindex)
                    if header == "paired_end":
                        paired_end = str(int(work.cell_value(row, colindex)))
                    if header == "paired_with":
                        paired_with = work.cell_value(row, colindex)
                    if header == "output_type":
                        output_type = work.cell_value(row, colindex)
                    if header == "flowcell_details":
                        cell = work.cell_value(row, colindex)
                        cell = cell.split(', ')
                        sub_object = {}
                        for i in cell:
                            pair = i.split(': ')
                            if pair[0] == 'machine':
                                if pair[1] == '@HWI-D00422' or pair[1] == '@HWI-ST1083' or pair[1] == '@HWI-70014499L' or pair[1] == '@HWI-700819F' or pair[1] == '@D3NW3HQ1':
                                    platform = 'Illumina HiSeq 2500'
                                elif pair[1] == '@HWI-ST484' or pair[1] == '@HWI-ST673' or pair[1] == '@D13608P1' or pair[1] == '@DC4RYQN1' or pair[1] == '@HWI-7001449L' or pair[1] == '@HISEQ1' or pair[1] == '@LYNLEY' or pair[1] == '@BRISCOE' or pair[1] == '@MONK' or pair[1] == '@TENNISON' or pair[1] == '@HAVERS':
                                    platform = 'Illumina HiSeq 2000'
                                elif pair[1] == '@MAGNUM' or pair[1] == '@ROCKFORD' or pair[1] == '@KOJAK' or pair[1] == '@COLUMBO' or pair[1] == '@SPADE' or pair[1] == '@GENTLY':
                                    platform = 'Illumina Genome Analyzer IIx'
                                elif pair[1] == '@K00242':
                                    platform = 'Illumina HiSeq 4000'
                                elif pair[1] == '@HWI-ST665' or pair[1] == '@HWI-EAS276' or pair[1] == '@HWI-EAS146' or pair[1] == '@HWI-EAS137R' or pair[1] == '@HWUSI-EAS552R' or pair[1] == '@USI-EAS28' or pair[1] == '@HWI-EAS279' or pair[1] == '@HWI-EAS146':
                                    platform = 'Illumina Genome Analyzer'
                                else:
                                    print "cannot find platform for " + pair[1]
                                    sys.exit()
                            pair[1] = pair[1].replace('\n','')
                            sub_object[pair[0]] = pair[1]
                        cell = [sub_object]
                        format = 'fastq'
                else:
                    if header == "replicate":
                        rep = ''
            else:
                if header == "path_to_file":
                    path = work.cell_value(row, colindex)
                    print header+':', path
                    file = path
                    temp = os.path.splitext(path)
                    if (temp[1] == '.gz'):
                        file = file.replace('.gz', '')
                        temp = os.path.splitext(file)
                    if (temp[1] == '.bam'):
                        format = 'bam'
                        if request_type != "patch":
                            if proggen == 'dm3':
                                #file = [path]
                                os.system("cp " + path + " ./temp")
                                #os.system("cp /data/dm/processed/dm3/" + path + " ./temp")
                                #search = os.popen("rsync -cP --list-only avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/dm/processed/dm3/2*/" + path).readlines()
                                #if "1 file to consider\n" in search:
                                #    os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/dm/processed/dm3/2*/" + path + " ./temp")
                                #else:
                                #    print "wrong number of files found"
                                #    print search
                                #    sys.exit()
                                file = os.popen("find ./temp/* -name " + os.path.basename(path)).readlines()
                                #file = os.popen("find /raid/modencode/dm/processed/dm3/2* -name " + path).readlines()
                                #path = file[0].rstrip()
                                path = "./temp/" + os.path.basename(path)
                                assembly = 'dm3'
                                os.system("sh makeBamsdm3.sh ./temp/")
                            elif proggen == 'dm6':
                                os.system("cp " + path + " ./temp")
                                #os.system("cp /data/dm/processed/dm6/" + path + " ./temp")
                                #search = os.popen("rsync -cP --list-only avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/dm/processed/dm6/2*/" + path).readlines()
                                #if "1 file to consider\n" in search:
                                #    os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/dm/processed/dm6/2*/" + path + " ./temp")
                                #else:
                                #    print "wrong number of files found"
                                #    print search
                                #    sys.exit()
                                #file = os.popen("find ./temp/* -name " + path).readlines()
                                #os.system("sshpass -f '../mycloud.password' rsync -v --progress sshd@128.135.219.201:/nfs/modern/modencode/dmel/processed/dm6/2*/" + path + " ./temp/")
                                file = os.popen("find ./temp/* -name " + os.path.basename(path)).readlines()
                                #file = os.popen("find /media/mybooklive/modencode/dmel/processed/dm6/2* -name " + path).readlines()
                                #path = "./temp/" + path
                                #path = file[0].rstrip()
                                path = "./temp/" + os.path.basename(path)
                                assembly = 'dm6'
                                #os.system("sh makeBamsdm6.sh ./temp/")
                            elif proggen == 'WS220':
                                os.system("cp " + path + " ./temp")
                                #search = os.popen("rsync -cP --list-only avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/ce/processed/WS220/old_data/" + path).readlines()
                                #if "1 file to consider\n" in search:
                                #    os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/ce/processed/WS220/old_data/" + path + " ./temp")
                                #else:
                                #    print "wrong number of files found"
                                #    print search
                                #    sys.exit()
                                file = os.popen("find ./temp/* -name " + os.path.basename(path)).readlines()
                                #path = "./temp/" + path
                                path = "./temp/" + os.path.basename(path)
                                assembly = 'ce10'
                            elif proggen == 'WS245':
                                os.popen("cp " + path + " ./temp")
                                #search = os.popen("rsync -cP --list-only avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/ce/processed/WS245/old_data/" + path).readlines()
                                #if "1 file to consider\n" in search:
                                #    os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:/glusterfs/data/modencode/WhiteLab_UniformProcessing/ce/processed/WS245/old_data/" + path + " ./temp")
                                #else:
                                #    print "wrong number of files found"
                                #    print search
                                #    sys.exit()
                                file = os.popen("find ./temp/* -name " + os.path.basename(path)).readlines()
                                #path = "./temp/" + path
                                path = "./temp/" + os.path.basename(path)
                                assembly = 'ce11'
                            else:
                                print 'Genome not recognized'
                                sys.exit()
                            if len(file) < 1:
                                print 'Error: no files found'
                                os.system("rmdir --ignore-fail-on-non-empty temp")
                                sys.exit()
                            if len(file) > 1:
                                print 'More than two bam files found: ',file
                                sys.exit()
                            path = file[0].rstrip()
                            #if proggen == 'dm3' or proggen == 'dm6':
                                #print 'copying: ', path
                                #os.system("cp " + path + " ./temp/")
                                #path = "./temp/" + os.path.basename(path)
                                #os.system("sh makeBamsdm3.sh ./temp/")
                            if proggen == 'WS245':
                                #print 'copying: ', path
                                #os.system("cp " + path + " ./temp/")
                                path = "./temp/" + os.path.basename(path)
                                os.system("sh makeBamsce11.sh ./temp/")
                    elif (temp[1] == ".txt" or temp[1] == '.fastq'):
                        format = 'fastq'
                        if request_type != "patch":
                            #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                            os.system("cp " + path + " ./temp/")
                            path = "./temp/" + os.path.basename(path)
                            os.system("perl Phred64_to_Phred33.pl " + path)
                    elif (temp[1] == '.wig'):
                       format = 'bigWig'
                       if request_type != "patch":
                           os.system("cp " + path + " ./temp/")
                           if (proggen == 'dm3'):
                               #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                               os.system("sh makeBigWigsdm3.sh ./temp/")
                               assembly = 'dm3'
                           elif (proggen == 'dm6'):
                               #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                               os.system("sh makeBigWigsdm6.sh ./temp/")
                               assembly = 'dm6'
                           elif (proggen == 'WS220'):
                               #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                               os.system("sh makeBigWigsce10.sh ./temp/")
                               assembly = 'ce10'
                           elif (proggen == 'WS245'):
                               #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                               os.system("sh makeBigWigsce11.sh ./temp/")
                               assembly = 'ce11'
                           else:
                               print("can't find assembly:" + assembly)
                               sys.exit()
                           path = "./temp/" + os.path.basename(path)
                           path = path.replace('.wig', '.bw')
                           print "File Converted to " + path
                    elif (temp[1] == '.regionPeak'):
                       format = 'bed'
                       if request_type != "patch":
                           #os.system("rsync -cP avictorsen@sullivan.opensciencedatacloud.org:" + path + " ./temp/")
                           os.system("cp  --no-preserve='all' " + path + " ./temp/")
                           if (proggen == 'dm3'):
                               os.system("sh makeBigBedsdm3.sh ./temp/")
                               assembly = 'dm3'
                           elif (proggen == 'dm6'):
                               os.system("sh makeBigBedsdm6.sh ./temp/")
                               assembly = 'dm6'
                           elif (proggen == 'WS220'):
                               os.system("sh makeBigBedsce10.sh ./temp/")
                               assembly = 'ce10'
                           elif (proggen == 'WS245'):
                               #os.system("sh makeBedsce11.sh ./temp/")
                               os.system("sh makeBigBedsce11.sh ./temp/")
                               assembly = 'ce11'
                           else:
                               print("can't find assembly:" + assembly)
                               sys.exit()
                           path = "./temp/" + os.path.basename(path)
                           print "new path_to_file:" + path
                    else:
                       print "Path not recognized"
                       sys.exit()
        if 'rep' in vars():
            if rep == '' and output_type != 'reads':
                step = DCC_pooled_pipeline[output_type]
            elif output_type != 'reads':
                step = DCC_rep_pipeline[output_type]
        elif output_type != 'reads':
            step = DCC_rep_pipeline[output_type]

        #compile and send to DCC
        DCC(locals(),OUTPUT,FAIL,PATCH)
        #if file format is bed, rerun with original bed file
        #sys.exit()
        if (format == 'bed'):
            print "\n\nRepeating submission with bigBed file\n"
            derived_from = [aliases]
            aliases = aliases.replace('-bed','-bigBed')
            print "aliases: "+aliases
            if rep == '':
                if output_type == "optimal idr threasholded peaks":
                    step = DCC_pooled_pipeline['optimal idr bigBed']
                else:
                    step = DCC_pooled_pipeline['bigBed']
            else:
                step = DCC_rep_pipeline['bigBed']
            if 'replaces' in vars():
                print "supersedes: ",
                for i, old in enumerate(replaces):
                    new = old.replace('-bed','-bigBed')
                    print new+", "
                    replaces[i] = new
            format = 'bigBed'
            path = path.replace('.gz','.bb')
            DCC(locals(),OUTPUT,FAIL,PATCH)


        ####Clean up
        os.system("rm -f ./temp/*")
    os.system("rmdir --ignore-fail-on-non-empty temp")

def DCC(d, OUTPUT, FAIL, PATCH):
    encValData = 'encValData'
    #compile data
    data = {
        "aliases": [d['aliases']],
        "dataset": d['exp'],
        "lab": d['my_lab'],
        "award": d['my_award'],
        "file_format": d['format']
	}
    ## add specific data to data array
    if ('derived_from' in d['headers']):
        if d['derived_from'] != None:
            data['derived_from'] = d['derived_from']
        if 'assembly' in d and data['file_format'] == 'bam':
            if d['assembly'] is 'dm3':
                data['derived_from'].append('ENCFF059UHX')
            if d['assembly'] is 'dm6':
                data['derived_from'].append('ENCFF479RCH')
            if d['assembly'] is 'ce10':
                data['derived_from'].append('ENCFF987UMF')
            if d['assembly'] is 'ce11':
                data['derived_from'].append('ENCFF586MOL')
    if 'replaces' in d:
        data['supersedes'] = d['replaces']
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
        if 'output_type' in d:
            if d['output_type'] == 'reads':
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
    if d['request_type'] != "patch":
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
#    if 'check' in sys.argv[5]:
#        return
#    sys.exit()
    r = requests.post(
        d['host'] + '/files',
        auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
        data=json.dumps(data),
        headers=DCCheaders,
    )
    if d['request_type'] != 'patch':
        print "\nposting metadata:",
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            #print "r:",r.json()
            print " Failed! Trying patch"
#    if d['request_type'] == 'patch':
#        print "removing md5sum, file_size, and submitted_file_name for update"
#        del data['md5sum']
#        del data['file_size']
#        del data['submitted_file_name']
    if d['request_type'] == 'patch' or 'status' in r.json():
        print "patching metadata:",
        s = requests.patch(#change to put to overwrite,patch to ammend
            d['host'] + '/' + d['aliases'],
            auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
            data=json.dumps(data),
            headers=DCCheaders,
        )
        try:
            s.raise_for_status()
        except requests.exceptions.HTTPError:
            print ' Failed!'
            print '\ndata: ', data
            print
            if 'r' in vars():
                print('Post attempt: %s %s' % (r.status_code, r.reason))
                print r.json()
                print
            print('Patch attempt: %s %s' % (s.status_code, s.reason))
            print s.json()
    print " Success!"
    if r.json()[u'status'] == 'success':
        print '  uuid: ',r.json()['@graph'][0]['uuid']
        temp = r.json()['@graph'][0]['uuid']
    elif s.json()[u'status'] == 'success':
        print '  uuid: ',s.json()['@graph'][0]['uuid']
        temp = s.json()['@graph'][0]['uuid']
        PATCH.write(d['aliases'])
        PATCH.write('\t')
        PATCH.write(temp)
        PATCH.write('\n')
    elif s.json()[u'status'] != 'success':
        FAIL.write(d['aliases'])
        FAIL.write('\t%s\t%s\n' % (s.status_code, s.reason))
    else:
        print "something went really wrong"
        sys.exit()
    ##### upload files
    ############### post ###############
    if temp != "" and d['request_type'] == 'post':
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
        #print t.json()
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
        print "\nUploading: ",
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
                #print("Upload failed with exit code %d" % e.returncode)
                #print "Retrying"
                time.sleep(2)
                i = i+1
                continue
        if err_after_4 is True:
            print 'Failed! %d' % e.returncode
            sys.exit()
        end = time.time()
        duration = end - start
        print" Uploaded in %.2f seconds" % duration
    ############# overwrite ################
    elif temp != "" and d['request_type'] == 'overwrite':
        ID = s.json()['@graph'][0]['accession']
        print "ID: " + ID
        print("Fetching credentials.")
        temp = s.json()['@graph'][0]['aliases'][0]
        OUTPUT.write(temp)
        OUTPUT.write('\t')
        temp = s.json()['@graph'][0]['uuid']
        OUTPUT.write(temp)
        OUTPUT.write('\n')
        renew_upload_credentials = "curl -X POST -H 'Accept:application/json' -H 'Content-Type:application/json' https://" + d['encoded_access_key'] + ":" + d['encoded_secret_access_key'] + "@www.encodeproject.org/files/" + ID + "/upload -d '{}'"
#        t = requests.patch(
#            d['host'] + d['aliases'],
#            auth=(d['encoded_access_key'], d['encoded_secret_access_key']),
#            data=json.dumps(data),
#            headers=DCCheaders,
#        )
#        try:
#            t.raise_for_status()
#        except:
#            print "t: ",t.json()
#            print "he's dead jim"
#            sys.exit();
#        print t.json()
#        print "new cred: "
#        print json.loads(os.popen(renew_upload_credentials).read())
        item = json.loads(os.popen(renew_upload_credentials).read())['@graph'][0]
        #POST file to S3
        creds = item['upload_credentials']
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': creds['access_key'],
            'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
            'AWS_SECURITY_TOKEN': creds['session_token'],
        })
        print "Uploading: "
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
                #print("Upload failed with exit code %d" % e.returncode)
                #print "Retrying"
                time.sleep(2)
                i = i+1
                continue
        if err_after_4 is True:
            print 'Failed! %d' % e.returncode
            sys.exit()
        end = time.time()
        duration = end - start
        print("Uploaded in %.2f seconds" % duration)
    #print s.json()
    else:
        return;
	#print 'temp failed'
        #sys.exit()
    return;

main()
