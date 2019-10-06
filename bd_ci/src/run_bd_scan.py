import subprocess
import logging
import os
import sys

BASE_DIRECTORY = "/qa/qa/arielwe/bd_vladi/blackduck/"
SCRIPT_PATH = os.getcwd() +"../" + "run_bd_scan_sh.sh"

def run_blackduck_scan():
    print ("start running blackduck scan")
    try:
        subprocess.call(SCRIPT_PATH, timeout=9000)
    except Exception as e:
        logging.error("ERROR while running blackduck scan with subprocess")
        sys.exit(1)

    print ("finish running blackduck scan")


def main():

    logging.basicConfig(filename=BASE_DIRECTORY + 'security_ci.log',
                        level="DEBUG",
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='a')
    run_blackduck_scan()

if __name__ == '__main__':
    main()
