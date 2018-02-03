# ADDRESSES
ECOMM_IP="http://10.3.$1.10"
COMM_IP="http://10.2.$1.75"
JENKINS_SWIFT_IP="10.2.$1.10"
JENKINS_WIN_IP="10.3.$1.20"
SMB_IP_1="10.2.$1.20"
SMB_IP_2="10.2.$1.30"
SMB_IP_3="10.2.$1.40"
FTP_IP="10.2.$1.20"
FTP_PORT="21"
SSH_IP="10.3.$1.10"
SSH_PORT="22"
ELASTIC_IP="10.2.$1.50"
ELASTIC_PORT="9000"
DNS_IP="10.2.$1.40"

# VARIABLES
WIN_USERNAME="administrator"
LINUX_USERNAME="root"
PASSWORD="Changeme-2018"
REMOTE_FILE_PATH="C:\inet\ftproot"
REMOTE_FILE_CONTENTS=""
SSH_COMMANDS="echo hi"
ELASTIC_INDEX=""
ELASTIC_DOCTYPE=""
BASE_DN="dc=team$1,dc=ists"

# CHECKS
python checks/comcenter/check.py -a $COMM_IP
python checks/ecomm/check.py -t 1 -a $ECOMM_IP
python checks/jenkins/check.py $JENKINS_SWIFT_IP $PASSWORD
python checks/jenkins/check.py $JENKINS_WIN_IP $PASSWORD
python checks/ftp/check.py $FTP_IP $FTP_PORT $WIN_USERNAME $PASSWORD $REMOTE_FILE_PATH $REMOTE_FILE_CONTENTS
python checks/ssh/check.py $SSH_IP $SSH_PORT $LINUX_USERNAME $PASSWORD "$SSH_COMMANDS"
#python checks/elastic/check.py $ELASTIC_IP $ELASTIC_PORT $ELASTIC_INDEX $ELASTIC_DOCTYPE

nslookup team$1.ists $DNS_IP >> /dev/null; [ $? = 0 ] && echo good || echo bad

ldapsearch -x -h $DNS_IP -p 389 -D $WIN_USERNAME@team$1.ists -b "$BASE_DN" -w $PASSWORD '(objectclass=User)' cn  >> /dev/null; [ $? = 0 ] && echo good || echo bad


# PINGS
ping -c 1 $ECOMM_IP
ping -c 1 $COMM_IP
ping -c 1 $JENKINS_SWIFT_IP
ping -c 1 $JENKINS_WIN_IP
ping -c 1 $SMB_IP_1
ping -c 1 $SMB_IP_2
ping -c 1 $SMB_IP_3
ping -c 1 $FTP_IP
ping -c 1 $SSH_IP
ping -c 1 $ELASTIC_IP