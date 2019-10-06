import argparse
import logging
import sys
import os
from shutil import copyfile


SOURCE_FILE_PATH = "../source"
PROJECT_NAME = "export PROJECT_NAME=\"project_name_tmp\""
PROJECT_VERSION = "export PROJECT_VERSION=\"project_version_tmp\""
BASE_DIRECTORY = "/qa/qa/arielwe/bd_vladi/blackduck/"
PROJECT_SRC_PATH = "export PROJECT_SRC_PATH=\"" + BASE_DIRECTORY + "folder_tmp\""

def main():

    #TODO ArgPasre
    parser = argparse.ArgumentParser(description='simple usage: --project NEO --username Arielwe \
    --password 12345678 --file /qa/qa/security/neo/neo-2.3.0-91.el7.tar.gz --debug yes')
    #TODO - change all choices
    parser.add_argument('--project',choices=['UFM','UFMAPL','NEO','MFT','HPCX'] , dest='project', help='select a project from list')
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


    logging.info("Start Script...")
    edit_source_file()
    copy_file_to_tmp()

def copy_file_to_tmp(project_name,file_path ):

    logging.info("start copy project file to tmp directory")
    directory_path = BASE_DIRECTORY + project_name
    logging.info("Add write/Read permission for directory")
    try:
        mode ="777"
        os.chmod(directory_path, mode)
    except Exception as e:
        logging.error("ERROR: Can't change permission for directory")
        sys.exit(1)

    logging.info("Copy file ")
    try:
        copyfile(file_path, directory_path)
        logging.info("Copy file succeeded")
    except Exception as e:
        logging.error("ERROR : copy file failed")
        sys.exit(1)
    logging.info("Copy file is done")




def edit_source_file(name, version, src_path):
    logging.info("start editing source file")

    project_name = PROJECT_NAME.replace("project_name_tmp",str(name).join("_AUTOMATION"))
    project_version = PROJECT_VERSION.replace("project_version_tmp",str(version))
    project_src_path = PROJECT_SRC_PATH.replace("folder_tmp",name)

    logging.info("Project name is:" + project_name)
    logging.info("Project version is: "+ project_version)
    logging.info("Project src path is: " + project_src_path)

    logging.info("Writing information into file:")
    try:
        with open(SOURCE_FILE_PATH, 'a') as file1:
            file1.write(project_name)
            file1.write((project_version))
            file1.write(project_src_path)
    except Exception as e:
        logging.error("ERROR while editing source file")
        sys.exit(1)

    logging.info("source file was written successfully")


if __name__ == '__main__':
    main()



