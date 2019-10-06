#!/bin/sh
#
# Scipt for executing a BlackDuck Scan
#
# USAGE:
# Execute on Linux machine
# Requires Java 8
# Execute in a directory where you have WRITE permissions
#

###  Functions - START
info(){
  echo "INFO:($(basename ${0})) $*"
}

error(){
  echo "ERROR:($(basename ${0})) $*"
}

die(){
  error $*
  exit 1
}

usage(){
  info "Usage: $(basename ${0}) SCAN_TYPE[full:fast]"
  die
}
###  Functions - END

### Check JAVA version
JAVA=$(which java)
if [ -z "${JAVA}" ]; then
  die "No JAVA found. Exiting with error"	
else
  info "Using JAVA: ${JAVA}"
  JAVA_VERSION=$(java -version 2>&1  | grep 'version' | awk '{print $3}' | sed s'/\"//g' )
  if [[ "${JAVA_VERSION}" =~ "1.8.0".* ]]; then
    info "JAVA Version: ${JAVA_VERSION}"
  else
    die "JAVA Version 1.8.0 or higher required. Found: ${JAVA_VERSION}"
  fi
fi

### Check Required Parameters
if [ -z ${SPRING_APPLICATION_JSON} ]; then
  die "No SPRING_APPLICATION_JSON found. Exiting with error"
fi
if [ -z ${PROJECT_NAME} ]; then
  die "No PROJECT_NAME found. Exiting with error"
fi
if [ -z ${PROJECT_VERSION} ]; then
  die "No PROJECT_VERSION found. Exiting with error"
fi
if [ -z ${PROJECT_SRC_PATH} ]; then
  die "No PROJECT_SRC_PATH found. Exiting with error"
fi

### Read Sript Parameters
# SCAN_TYPE=${1} && shift
# if [ -z ${SCAN_TYPE} ]; then
#   usage
# fi

### Download detect
WORK_DIR=$(pwd)
for DIR in bin output report log
do
  if [ ! -d "${WORK_DIR}/${DIR}" ]; then
    info "Creating directory: ${WORK_DIR}/${DIR}"
    mkdir -p ${WORK_DIR}/${DIR}
  fi
done

if [ ! -e "${WORK_DIR}/detect.sh" ]; then
  curl -O https://detect.synopsys.com/detect.sh
  chmod +x detect.sh
fi

### Run detect
export DETECT_SCRIPT=${WORK_DIR}/detect.sh
export DETECT_JAR_DOWNLOAD_DIR=${WORK_DIR}/bin
export DETECT_VERSION_KEY="DETECT_LATEST_5"
#export DETECT_PROJECT_FLAGS="--detect.project.name=${PROJECT_NAME} --detect.project.version.name=${PROJECT_VERSION} --detect.source.path=${PROJECT_SRC_PATH}"
export DETECT_PROJECT_FLAGS="--detect.project.name=${PROJECT_NAME} --detect.project.version.name=${PROJECT_VERSION} --detect.binary.scan.file.path=${PROJECT_SRC_PATH}"
export DETECT_REPORT_FLAGS="--detect.risk.report.pdf=true --detect.report.timeout=30000 --detect.risk.report.pdf.path=${WORK_DIR}/report"
export DETECT_GENERAL_FLAGS="--blackduck.trust.cert=true --detect.output.path=${WORK_DIR}/output"
export DETECT_SCAN_FLAGS="--detect.project.detector=BINARY_SCAN --detect.tools=BINARY_SCAN --detect.blackduck.signature.scanner.disabled=true"
#export DETECT_SCAN_FLAGS="--detect.blackduck.signature.scanner.snippet.mode=true --detect.excluded.detector.types=nuget,bazel,docker --detect.tools=SIGNATURE_SCAN,DETECTOR"
export LOG_FILE=${WORK_DIR}/log/${PROJECT_NAME}_${PROJECT_VERSION}_$(date '+%Y-%m-%d-%H%M%S').log

info "Running BlackDuck scan in: ${WORK_DIR}"
info "Execution log file: ${LOG_FILE}"
${DETECT_SCRIPT} ${DETECT_GENERAL_FLAGS} ${DETECT_PROJECT_FLAGS} ${DETECT_REPORT_FLAGS} ${DETECT_SCAN_FLAGS} > ${LOG_FILE}
info "The BlackDuck Scan completed. Exit code: $?"
