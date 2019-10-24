# This file just clone the repository to Base Directory and start 'bd_precondistion.py'
import argparse
import logging
import os
import sys
import subprocess

BASE_DIRECTORY = "/tmp/"
BD_MANGER_PATH = '/tmp/Security_CI/bd_ci/src/bd_manager.py'

def main():
    #TODO ArgPasre
    parser = argparse.ArgumentParser(description='simple usage: --project NEO \
     --file /qa/qa/security/neo/neo-2.3.0-91.el7.tar.gz')
    #TODO - change all choices
    parser.add_argument('--project',choices=['UFM','MOFED','NEO','MFT','UFMAPL','MLNX_OS','HPCX'] , dest='project', help='select a project from list')
    parser.add_argument('--version', help='product version',dest='version', required=True)
    parser.add_argument('--file', help='file to scan',dest='file', required=True)

    parser.add_argument('--debug', dest='debug', help='change to debug mode')

    args = parser.parse_args()

    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(filename=BASE_DIRECTORY + 'security_ci.log',
                        level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='w')
    print("start script for blackduck with these params:" + "Project = " + args.project + '\n'\
          + "Version = " + args.version + "\n" + "File = " + args.file + "\n" )
    print("Start the script")
    clone_repository()
    run_bd_manager(args.project ,args.version, args.file)

def run_bd_manager(project, version, file):

    print("start running bd manager")
    try:
        cmd = BD_MANGER_PATH + ' ---project ' + project + " --version " + version + ' --file ' + file
        print("running CMD is : " + cmd)
        # subprocess has no attribute run even when i used Python 3.6.6
        #result = subprocess.run(SCRIPT_PATH    , stdout=subprocess.PIPE)
        result_b = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
        try:
            logging.info("Convert bytes to string")
            result = result_b.decode("utf-8")
        except Exception as e:
            logging.error("ERROR on converting bytes to string" + str(e))
            exit(1)

    except Exception as e:
        logging.error("ERROR while running blackduck scan with subprocess" + str(e))
        sys.exit(1)
    print("run bd is Done!")

def clone_repository():


    path  = BASE_DIRECTORY
    clone = "git clone https://github.com/WeiserAriel/Security_CI.git"
    print("Cloning the repository to :" + clone)
    try:
        #os.system("ssh -p 3tango root@smg-ib-svr040") #i will run it on the local machine.
        os.chdir(path) # Specifying the path where the cloned project needs to be copied
        os.system(clone) # Cloning
    except Exception as e:
        print("ERROR: Exception received while trying to clone the repository to : " + BASE_DIRECTORY + " error message:" + str(e))
        exit(1)

if __name__ == '__main__':
    main()