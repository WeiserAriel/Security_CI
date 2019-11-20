#!/bin/sh                                                                                                                 
#                                                                                                                         
# Scipt for executing a BlackDuck Scan                                                                                    
#                                                                                                                         
# USAGE:                                                                                                                  
# Execute on Linux machine                                                                                                
# Requires Java 8                                                                                                         
# Execute in a directory where you have WRITE permissions                                                                 
#                                                                                                                         

### Constants - START
BINARY_SCAN_TYPE="binary"
SOURCE_SCAN_TYPE="source"
### Constants - END      
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
  info "Usage:"
  info "Source Scan: $(basename ${0})"
  info "Binary Scan: $(basename ${0}) binary"
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
SCAN_TYPE=${1}           
if [ -z ${SCAN_TYPE} ]; then
  SCAN_TYPE=${SOURCE_SCAN_TYPE}
  if [ "${SCAN_TYPE}" != "${BINARY_SCAN_TYPE}" -a "${SCAN_TYPE}" != "${SOURCE_SCAN_TYPE}" ]; then
    usage                                                                                        
    die "Unsupported scan type: ${SCAN_TYPE}"                                                    
  fi                                                                                             
fi                                                                                               

### Validate PROJECT_SRC_PATH
if [ "${SCAN_TYPE}" = "${SOURCE_SCAN_TYPE}" -a ! -d ${PROJECT_SRC_PATH} ]; then
  die "Source scan failed. PROJECT_SRC_PATH should be directory"
fi
if [ "${SCAN_TYPE}" = "${BINARY_SCAN_TYPE}" -a -d ${PROJECT_SRC_PATH} ]; then
  die "Binary scan failed. PROJECT_SRC_PATH should be file"
fi

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
if [ "${SCAN_TYPE}" = "${SOURCE_SCAN_TYPE}" ]; then
  export DETECT_PROJECT_FLAGS="--detect.project.name=${PROJECT_NAME} --detect.project.version.name=${PROJECT_VERSION} --detect.source.path=${PROJECT_SRC_PATH}"
else
  export DETECT_PROJECT_FLAGS="--detect.project.name=${PROJECT_NAME} --detect.project.version.name=${PROJECT_VERSION} --detect.binary.scan.file.path=${PROJECT_SRC_PATH}"
fi
export DETECT_REPORT_FLAGS="--detect.risk.report.pdf=true --detect.report.timeout=30000 --detect.risk.report.pdf.path=${WORK_DIR}/report"
export DETECT_GENERAL_FLAGS="--blackduck.trust.cert=true --detect.output.path=${WORK_DIR}/output"
if [ "${SCAN_TYPE}" = "${SOURCE_SCAN_TYPE}" ]; then
  export DETECT_SCAN_FLAGS="--detect.blackduck.signature.scanner.snippet.mode=true --detect.excluded.detector.types=nuget,bazel,docker --detect.tools=SIGNATURE_SCAN,DETECTOR"
else
  export DETECT_SCAN_FLAGS="--detect.blackduck.signature.scanner.disabled=true --detect.project.detector=BINARY_SCAN --detect.tools=BINARY_SCAN"
fi
export LOG_FILE=${WORK_DIR}/log/${PROJECT_NAME}_${PROJECT_VERSION}_$(date '+%Y-%m-%d-%H%M%S').log

info "Running BlackDuck scan in: ${WORK_DIR}"
info "Execution log file: ${LOG_FILE}"
${DETECT_SCRIPT} ${DETECT_GENERAL_FLAGS} ${DETECT_PROJECT_FLAGS} ${DETECT_REPORT_FLAGS} ${DETECT_SCAN_FLAGS} > ${LOG_FILE}
info "The BlackDuck Scan completed. Exit code: $?"
