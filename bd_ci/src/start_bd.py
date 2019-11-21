# This file just clone the repository to Base Directory and start 'bd_precondistion.py'
import argparse
import logging
import os
import sys
import subprocess
import shutil


CURRENT = os.path.dirname(os.path.abspath(__file__)) + os.sep
BASE_DIRECTORY = "/tmp/"
BASE_BD_MANAGER_PATH = '/tmp/Security_CI/'
SRC_DIR = BASE_BD_MANAGER_PATH + 'bd_ci/src/'
BD_MANGER_PATH = BASE_BD_MANAGER_PATH +'bd_ci/src/bd_manager.py'


def main():
    print("Start the script start_bd.py")
    #TODO ArgPasre
    parser = argparse.ArgumentParser(description='simple usage: --project NEO \
     --file /qa/qa/security/neo/neo-2.3.0-91.el7.tar.gz')
    #TODO - change all choices
    parser.add_argument('--project',choices=['UFM','MOFED','NEO','MFT','UFMAPL','MLNX_OS','HPCX','OPENSM','SHARP','IBUTILS2'] , dest='project', help='select a project from list')
    parser.add_argument('--version', help='product version',dest='version', required=True)
    parser.add_argument('--file', help='file to scan',dest='file', required=True)
    parser.add_argument('--binary', help='binary scan of one file',dest='binary')




    args = parser.parse_args()

    print("start script for blackduck with these params:\n" + "Project = " + args.project + '\n'\
          + "Version = " + args.version + "\n" + "File = " + args.file + "\n" )

    check_folder_size_for_scan(args.file)
    clone_repository()
    run_bd_manager(args.project ,args.version, args.file, args.binary)

def check_folder_size_for_scan(file):
    print("Check that source code is Smaller than 3.5GB")
    try:
        if os.path.isdir(file):
            size_in_bits = getFolderSize(file)
            h_size = human(size_in_bits)

            if 'GB' in h_size:
                try:
                    num_of_gb = str(h_size).split('GB')[0]
                    if float(num_of_gb) > float(3.5):
                        print("Your Directory : " + str(file) + "is  greater than 3.5GB !")
                        exit(1)
                except Exception as e:
                    print("ERROR: Exception was thrown in check folder size")

            print("Size of the directory is : " + str(h_size))
        else:
            print("path given is a regular file..checking the size of the file")
            size_in_bytes = os.path.getsize(file)
            if float(size_in_bytes) > float(1000000000*3.5):
                print("File size is greater than 3.5GB")
                exit(1)
            print("Size of the given file is OK ! ")
    except Exception as e:
        print("ERROR : got exeception in check folder size for scan" + str(e))
        exit(1)



def getFolderSize(p):
    from functools import partial
    prepend = partial(os.path.join, p)
    return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])


def human(size):

    B = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"
    UNITS = [B, KB, MB, GB, TB]
    HUMANFMT = "%f %s"
    HUMANRADIX = 1024.

    for u in UNITS[:-1]:
        if size < HUMANRADIX : return HUMANFMT % (size, u)
        size /= HUMANRADIX

    return HUMANFMT % (size,  UNITS[-1])





def run_bd_manager(project, version, file, binary):

    print("start running bd manager")
    try:
        if binary:
            cmd = "python " + BD_MANGER_PATH + ' --project ' + project + " --version " + version + ' --file ' + file + ' --binary ' + binary + ' &'
        else:
            cmd = "python " + BD_MANGER_PATH + ' --project ' + project + " --version " + version + ' --file ' + file + ' &'
        print("running CMD in in the background :\n " + cmd +'\n')
        os.system(cmd)
        #result_b = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        '''
        try:
            print("Convert bytes to string")
            result = result_b.decode("utf-8")
        except Exception as e:
            print("ERROR on converting bytes to string" + str(e))
            exit(1)
            '''

    except Exception as e:
        print("ERROR while running blackduck scan with subprocess" + str(e))
        sys.exit(1)
    print("Printing results from bd_manager.py\n" )
    #print(result_b +"'\n\n\n")
    print("run bd is Done! results will be available in 1h !")

def clone_repository():


    path  = BASE_DIRECTORY
    clone = "git clone https://github.com/WeiserAriel/Security_CI.git"
    print("Cloning the repository to :" + clone)
    try:
        #os.system("ssh -p 3tango root@smg-ib-svr040") #i will run it on the local machine.
        if os.path.exists(BASE_BD_MANAGER_PATH):
            print("Repository was exist on server before the script started. removing it. ")
            shutil.rmtree(BASE_BD_MANAGER_PATH)
        os.chdir(path) # Specifying the path where the cloned project needs to be copied
        os.system(clone) # Cloning
    except Exception as e:
        print("ERROR: Exception received while trying to clone the repository to : " + BASE_DIRECTORY + " error message:" + str(e))
        exit(1)

    set_correct_permission()

def set_correct_permission():

    print("Change permission for all source files to +x")
    for file in os.listdir(SRC_DIR):
        if file.endswith(".py"):
            try:
                tmp_file = os.path.join(SRC_DIR, file)
                print("chaning permission for "  + tmp_file)
                os.chmod(tmp_file,777)
            except Exception as e:
                print("ERROR : Execption received on set correct permissions to file " + str(e))
                exit(1)
    print("Change permission for all files are done. ")

if __name__ == '__main__':
    main()
