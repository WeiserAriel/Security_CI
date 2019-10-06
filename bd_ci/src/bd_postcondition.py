import logging
import shutil
import sys

BASE_DIRECTORY = "/qa/qa/arielwe/bd_vladi/blackduck/"

def main()
    logging.basicConfig(filename=BASE_DIRECTORY + 'security_ci.log',
                        level="DEBUG",
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filemode='a')

    clear_all_repository()

def clear_all_repository()
    directory_path = BASE_DIRECTORY + "bd_ci"
    logging.info("Removing entire repository repository from ")
    try:
        shutil.rmtree(directory_path)
    except Exception as e:
        logging.error("ERROR Couldn't remove repository")
        sys.exit(1)
    logging.info("Repository was removed")


if __name__ == "__main__":
    main()
