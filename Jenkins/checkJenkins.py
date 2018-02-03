#!/usr/bin/python3
import traceback
import requests
import jenkins
import sys
import time
import re

TEAM_EXT_IP = "10.3.x.20"
CHECK_TIMEOUT = 10
CHECK_USERNAME = "scoring"
CHECK_BUILD_NAME = "ShipBuilder"
CHECK_WINDOWS = "jobs/windows.xml"
CHECK_LINUX = "jobs/bsd.xml"
CHECK_FLAG = 'CHECK'
API_TOK = "GPNNKHLAHV"
API_SHIP_URL = "http://10.0.20.21:6000"
HASHES = ["b6589fc6ab0dc82cf12099d1c2d40ab994e8410c",
"356a192b7913b04c54574d18c28d46e6395428ab",
"da4b9237bacccdf19c0760cab7aec4a8359010b0",
"77de68daecd823babbb58edb1c8e14d7106e83bb",
"1b6453892473a467d07372d45eb05abc2031647a",
"ac3478d69a3c81fa62e60f5c3696165a4e5e6ac4",
"c1dfd96eea8cc2b62785275bca38ac261256e278",
"902ba3cda1883801594b6e1b452790cc53948fda",
"fe5dbbcea5ce7e2988b8c69bcfdfde8904aabc1f",
"0ade7c2cf97f75d009975f4d720d1fa6c19f4897",
"b1d5781111d84f7b3fe45a0852e59758cd7a87e5",
"17ba0791499db908433b80f37c5fbc89b870084b"]

def connect(ip, passwd):
    '''Make a connection to the jenkins server at IP
    '''
    user = CHECK_USERNAME
    url = "http://{}:8080/".format(ip)
    print("[*] Attempting to login via {}:{}".format(user, passwd))
    return jenkins.Jenkins(url, user, passwd, timeout=CHECK_TIMEOUT)

def submitJob(ip, password):
    '''Submit a job to the server. If windows then submit windows job,
    if linux, submit linux job
    '''
    jobName = CHECK_BUILD_NAME
    # Conenct to the server
    server = connect(ip, password)
    
    # Check if job exists. If so, delete it
    if server.job_exists(jobName):
        server.delete_job(jobName)
    # Get the right XML file
    if getHostname(ip) == "wolf":
        # Load windows config
        xmlFile = CHECK_WINDOWS
        jobType = "Windows"
    else:
        # Read linux config
        xmlFile = CHECK_LINUX
        jobType = "Linux"
    # Read the XML and submit it as a job
    xml=open(xmlFile, 'r').read()
    server.create_job(jobName, xml)
    # Build the job
    server.build_job(CHECK_BUILD_NAME)
    print("[+] Submitted {} job to host".format(ip, jobType))


def checkJob(ip, password):
    '''wait for the build to finish then return status
    '''
    success='SUCCESS'
    jobName = CHECK_BUILD_NAME
    # connect to the server
    server = connect(ip, password)
    # Wait for the job to finish
    count = 0
    while jobName in [d['name'] for d in server.get_running_builds()]:
        count += 1
        if count > 12:
            print("[-] waiting too long")
            exitFailed()
        time.sleep(10)
        print("[*] waiting on build...")
        
    # get the last build number (name of the build to get)
    isPass = False
    count = 0
    while not isPass:
        if count > 10:
            raise Exception("Failing a bunch")
        try:
            build_num = server.get_job_info(
                CHECK_BUILD_NAME)['lastBuild']['number']
            isPass = True
        except:
            count += 1
            time.sleep(5)
            
    # retrieve the output of the build (name of build, number of that build)
    output = server.get_build_console_output(CHECK_BUILD_NAME,
        build_num)
    # ensure output contains success and whiteteamKEY
    if success not in output:
        print("[-] Build failed")
        raise Exception("The build has failed: Did not compile")
    if CHECK_FLAG not in output:
        print("[-] Build failed")
        raise Exception("The build has failed: Missing scoring flag")
    # Find the flag in the output
    try:
        flag = re.findall('==== .+', output)
        flag = flag[0]
    except:
        flag = "NOFLAGFOUND"
    return incrementShips(ip, flag)


def incrementShips(ip, flag):
    '''Determine the type of ship based on the IP
    Activate on a certain team based on the flag
    '''
    # Determine the team number based on the flag
    try:
        teamNum = HASHES.index(flag[4:].strip())
        print("[*] Getting team from flag")
    except:
        teamNum = ip.split(".")[2]
        print("[*] Getting team from IP")
    # Check if we are building Bombers or Guardians
    if getHostname(ip) == "wolf":
        # Wolf makes bombers
        shipType = "bomber"
    else:
        # Vega makes guardians
        shipType = "guardian"

    data = { "value": 1 }
    url = API_SHIP_URL
    endpoint = "teams/{}/{}".format(teamNum, shipType)

    try:
        apiRequest(url, endpoint, data=data)
        print("[+] Build {} for team {}".format(shipType, teamNum))
        return True
    except Exception as e:
        print("[!] Error building ships: {}".format(e))
        raise e

def getHostname(ip):
    '''Convert an IP address to a hostname
    '''
    if ip.split(".")[:2] == TEAM_EXT_IP.split(".")[:2]:
        return "wolf"
    else:
        return "vega"

def apiRequest(url, endpoint, data=None, method='POST'):
    url += "/" + endpoint
    cookies = {'token': API_TOK}
    if method == 'POST':
        resp = requests.post(url, json=data, cookies=cookies)
    else:
        resp = requests.get(url, cookies=cookies)
    
    if resp.status_code == 400:
        msg = "Bad request sent to API"
        raise Exception(msg)
    if resp.status_code == 403:
        msg = resp.json()['error']
        raise Exception(msg)
    elif resp.status_code != 200:
        msg = "API returned {} for /{}".format(resp.status_code, endpoint)
        raise Exception(msg)
    resp_data = resp.json()
    return resp_data

def main():
    try:
        if len(sys.argv) < 3:
            raise Exception("Please provide ip and password")
        ip = sys.argv[1]
        password = sys.argv[2]
        submitJob(ip, password)
        checkJob(ip, password)
        print("[+] SUCCESS")
        return True
    except Exception as e:
        print("[!] " +str(e))
        traceback.print_exc()
        print("[-] FAILED")
        return False

if __name__ == '__main__':
    main()
