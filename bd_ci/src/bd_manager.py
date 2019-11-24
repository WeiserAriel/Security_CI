import argparse
import logging
import sys
import os
import tarfile
import shutil
import subprocess
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# TODO - need to clone repository to /tmp/ci_security/
#REPOSITORY CONTANTS:

BASE_DIRECTORY = "/tmp/Security_CI/"
SOURCE_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep +"../"  + "config"
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep +"../" + "run_bd_scan.sh"
SCRIPT_PATH_BIN = os.path.dirname(os.path.abspath(__file__)) + os.sep +"../" + "run_bd_scan.sh binary"

#SOURCE FILE CONSTANTS:
PROJECT_NAME = "export PROJECT_NAME=project_name_tmp"
PROJECT_VERSION = "export PROJECT_VERSION=project_version_tmp"
PROJECT_SRC_PATH = "export PROJECT_SRC_PATH=" + BASE_DIRECTORY + "folder_tmp"



#Examples: --project MOFED --file /mswg/release/ofed/OFED-internal-4.6-3.7.7.2/SRPMS/ --version MOFED4.6.3
#Examples: --project NEO --file/auto/UFM/NEO/release/NEO-2.5.0/NEO-2.5.0-4/rhel7/neo-2.5.0-4.el7.tar.gz --version NEO_2_5_0
#Examples: --project MLNX_OS --file onyx-X86_64-3.8.2004.img
#Examples: --project UFMAPL --file image-ufm_appliance-x86_64-UFMAPL_4.1.5.2_UFM_6.2.6.2-20190911-130519.img
#Examples:  --project MFT --file /mswg/release/mft/mft-4.13.0/mft-4.13.0-104/linux/mft-4.13.0-104/RPMS/mft-4.13.0-104-x86-rpm.tgz --version MFT_4_13_0_104_RPM
#Examples: --project UFMAPL --file  /mswg/release/ufm/appliance/UFMAPL_4.1.5.2_UFM_6.2.6.2/image-ufm_appliance-x86_64-UFMAPL_4.1.5.2_UFM_6.2.6.2-20190911-130519.img --version UFMAPL_4_1_5_ISO
#Examples: --project HPCX --file  /hpc/noarch/HPCX/released/v2.4.1/hpcx-v2.4.1.0-gcc-MLNX_OFED_LINUX-4.5-1.0.1.0-redhat7.6-x86_64.tbz --version HPCX2_4_1-tgz

def main():
    print("Start Script from bd_manager.py")
    #TODO ArgPasre
    parser = argparse.ArgumentParser(description='simple usage: --project NEO \
     --file /qa/qa/security/neo/neo-2.3.0-91.el7.tar.gz')
    #TODO - change all choices
    parser.add_argument('--project',choices=['UFM','MOFED','NEO','MFT','UFMAPL','MLNX_OS','HPCX','OPENSM','IBUTILS2','SHARP'] , dest='project', help='select a project from list')
    parser.add_argument('--version', help='product version',dest='version', required=True)
    parser.add_argument('--file', help='file to scan',dest='file', required=True)
    parser.add_argument('--binary', help='binary scan of one file',dest='binary')

    args = parser.parse_args()

    #TODO - checking env variables with os module instead of 'source' command 
    configure_env_vars(args.project, args.version, args.file, args.binary)
    #edit_source_file(args.project, args.version, args.file, args.binary)
    #if it's MOFED i need to take sources and untar them for arg.file.
    directory_path = copy_file_to_tmp(args.project, args.file, args.binary)
    #load_source_file(args.project)
    verify_env_var()
    run_blackduck_scan(args.binary)
    clear_all_repository()
    send_email(args.project ,args.version, args.file)
    print("BD ENDS SUCCUSSFULLY!!!\n\n ")
    exit(0)

def configure_env_vars(project, version, file, binary):
    try:
        print('setting env variables')
        os.environ["SPRING_APPLICATION_JSON"] = r"""{"blackduck.url":"https://blackduck.mellanox.com/","blackduck.api.token":"NjYyNTZjOTAtMGE4Ni00ZTcwLWE4MWMtNDkwYTEwMmZmNDViOmJkNTQ1ZDRjLTExYzAtNGI2Yy05Y2FiLTA0ZDNiZjdlNDMwYg=="}"""
        os.environ["PROJECT_NAME"] = project
        os.environ["PROJECT_VERSION"] =version
        os.environ["PROJECT_SRC_PATH"] =file


        print("Project name is:" + project)
        print("Project version is: "+ version)
        print("Project src path is: " + file)
    except Exception as e:
        print('ERROR : Exception received in ENV Variables configuration' + str(e))
        sys.exit(1)
    

    print("source file was written successfully")

def verify_env_var():
    vars = ['SPRING_APPLICATION_JSON','PROJECT_NAME','PROJECT_VERSION','PROJECT_SRC_PATH']
    
    for variable in vars:
        
        tmp = '$' + variable
        cmd = 'echo ' + tmp
        try:
            
            result_b = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
            result = result_b.decode("utf-8")
            if not result:
                print('ENV variable ' + tmp + ' is empty')
                sys.exit(1)
            else:
                print('checking Env variable : ' + tmp + ' = ' +result )
        except Execption as e:
            
            print('ERROR: got exception during verify env variables ' + str(e) )
            sys.exit(1)
    print('ENV variables check is finished successfully')
    
def send_email(project ,version, file):

    print("Sending Email to 'arielwe@mellanox.com to notify process complete")
    try:
        fromaddr = 'blackduck-scanner@mellanox.com'
        toaddr = 'arielwe@mellanox.com'
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "BlackDuck Results - " + str(version)
        body = "Project = " + str(project) +'\n' + "Version = " + str(version) + '\n' + "File = " + str(file) + '\n'
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("memory.tester1234@gmail.com", "2wsx@WSX")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
    except Exception as e:
        print("ERROR:Execption raised while sending an email")
        exit(1)


def copy_single_file(file_path,dst_directory_path):
    file_name = str(file_path).split('/').pop()
    dst_full_directory_path = dst_directory_path + file_name
    shutil.copyfile(file_path, dst_full_directory_path)
    
def copy_file_to_tmp(project_name,file_path,binary_scan ):  

    print("start copy project file to tmp directory")
    dst_directory_path = BASE_DIRECTORY + project_name +'/'
    print("Add write/Read permission for directory")
    try:
        mode = 777
        if not os.path.isdir(dst_directory_path):
            os.mkdir(dst_directory_path)
        os.chmod(dst_directory_path, mode)
        #os.chmod(file_path,mode)
    except Exception as e:
        print("ERROR: Can't change permission for directory" + str(e))
        sys.exit(1)
    print("Add write/Read permission for directory ended successfully")
    try:
        #for MOFED project we need to copy a directory and not a file:
        #example : file path = /mswg/release/ofed/OFED-internal-4.6-3.7.7.2/SRPMS/
        #project_arr = ['MOFED','MFT','HPCX','SHARP','OPENSM','IBUTILS2']
        #if project_name in project_arr:
        if binary_scan:
            print('binary scan is selected. copy file to tmp directory')
            # adding the name of the file to the directory path
            copy_single_file(file_path,dst_directory_path)
            print("Copy file for binary scan succeeded")
        else:  
            print(" source scan is chosen, copy all directoy to destination")
            print("Copy source files to :" + str(dst_directory_path) + "( This might take few minutes )")
            print("file_path = " + file_path + "\n" + "dst_full : " + dst_directory_path )
            print("check if file given is dirctory or regular file")
            if os.path.isdir(file_path):
                print ("given file is directory")
                copytree_helper(file_path, dst_directory_path)
                print("Copy directory for source scan succussfully")
            else:
                print("given file is a regular file ")
                copy_single_file(file_path,dst_directory_path)
                print("Copy single file for source scan succussfully")
           
    except Exception as e:

        print("ERROR : copy file failed" + str(e))
        print (str(e))
        sys.exit(1)
    print("Copy file is done")
    return dst_directory_path

def copytree_helper(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def load_source_file(project):
    print ("loading source file from : " + SOURCE_FILE_PATH)
    #w/o for ubuntu server in hpcx project
    print("project given is : " + project )
    if project == 'HPCX':
        cmd = '. ' + SOURCE_FILE_PATH
    else:
        cmd = 'source ' + SOURCE_FILE_PATH
    print('cmd is ' + cmd )
    try:
        for attempt in [1,2]:
            print('trying to load the source file #' + str(attempt))
            subprocess.call(cmd, shell=True)
            print('sleep 5 seconds')
            time.sleep(5)
    except Exception as e:
        print("ERROR while running loading source file with subprocess" + str(e))
        sys.exit(1)

    print ("loading source file is ended successfully")

def clear_all_repository():
    directory_path = BASE_DIRECTORY
    print("Removing entire repository repository from ")
    try:
        shutil.rmtree(directory_path)
    except Exception as e:
        print("ERROR Couldn't remove repository")
        sys.exit(1)
    print("Repository was removed")

def edit_source_file(name, version, src_path,binary):
    logging.info("start editing source file")

    project_name = PROJECT_NAME.replace("project_name_tmp",'\"' +str(name))  + '\"'
    project_version = PROJECT_VERSION.replace("project_version_tmp",'\"' + str(version)) + '\"'
    if not binary:
        project_src_path_arr = str(PROJECT_SRC_PATH.replace("folder_tmp",  name)).split('=')
        project_src_path = project_src_path_arr[0] +'=\"'+ project_src_path_arr[1]  +'\"'
    else:
        file_name = src_path.split('/')[-1]
        project_src_path_arr = str(PROJECT_SRC_PATH.replace("folder_tmp",  name)).split('=')
        project_src_path = project_src_path_arr[0] +'=\"'+ project_src_path_arr[1] + os.sep + file_name +'\"'
        

    print("Project name is:" + project_name)
    print("Project version is: "+ project_version)
    print("Project src path is: " + project_src_path)

    print("Writing information into file:")
    try:
        with open(SOURCE_FILE_PATH, 'a') as file1:
            file1.write(project_name+'\n')
            file1.write((project_version + '\n'))
            file1.write(project_src_path + '\n')
    except Exception as e:
        print("ERROR while editing source file" + str(e))
        sys.exit(1)

    print("source file was written successfully")


def run_blackduck_scan(binary):
    
    try:
        print("Check if binary scan was selected ")
        if binary:
            cmd = SCRIPT_PATH_BIN
            print("binary scan was selected. \n cmd is : " + cmd)
        else:
            cmd = SCRIPT_PATH
            print("source scan was select. \n cmd is : "+ cmd)
        print("start running blackduck scan ( NOTE : it can take between 30-80 minutes )")
        # subprocess has no attribute run even when i used Python 3.6.6
        #result = subprocess.run(SCRIPT_PATH    , stdout=subprocess.PIPE)
        result_b = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        try:
            print("Convert bytes to string")
            result = result_b.decode("utf-8")
        except Exception as e:
            print("ERROR on converting bytes to string" + str(e))
            exit(1)

    except Exception as e:
        print("ERROR while running blackduck scan with subprocess" + str(e))
        sys.exit(1)

    print("finish running subprocess for blackduck run")
    if 'Exit code: 0' in result:
        print("Blackduck scan ran successfully with exit code 0")
    else:
        print("ERROR: blackduck scan failed. exit code is not 0 !" + str(result))

if __name__ == '__main__':
    main()



