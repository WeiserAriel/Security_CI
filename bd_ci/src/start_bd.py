# This file just clone the repository to Base Directory and start 'bd_precondistion.py'
import argparse
import logging
import os
import sys
import subprocess
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    parser.add_argument('--project',choices=['UFM','MOFED','NEO','MFT','UFMAPL','MLNX_OS','HPCX'] , dest='project', help='select a project from list')
    parser.add_argument('--version', help='product version',dest='version', required=True)
    parser.add_argument('--file', help='file to scan',dest='file', required=True)
    parser.add_argument('--debug', help='verbosity',dest='debug')



    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(filename=CURRENT + 'bd_ci.log',
                        level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='w')
    print("start script for blackduck with these params:\n" + "Project = " + args.project + '\n'\
          + "Version = " + args.version + "\n" + "File = " + args.file + "\n" )

    clone_repository()
    run_bd_manager(args.project ,args.version, args.file)
    send_email(args.project ,args.version, args.file)
    print("BD ENDS SUCCUSSFULLY!!!\n\n ")

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

def run_bd_manager(project, version, file):

    print("start running bd manager")
    try:
        cmd = "python " + BD_MANGER_PATH + ' --project ' + project + " --version " + version + ' --file ' + file
        print("running CMD is : " + cmd)
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
    print("run bd is Done!")

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