#!/usr/bin/python3
import traceback
import requests
import jenkins
import sys
import time

TEAM_COUNT = 5
TEAM_EXT_IP = "10.3.x.20"
CHECK_TIMEOUT = 10
CHECK_USERNAME = "scoring"
CHECK_BUILD_NAME = "ShipBuilder"
CHECK_WINDOWS = "jobs/windows.xml"
CHECK_LINUX = "jobs/bsd.xml"
CHECK_FLAG = 'hi'
API_TOK = "GPNNKHLAHV"
API_SHIP_URL = "http://10.0.20.21:6000"
HASHES = ["c4ca4238a0b923820dcc509a6f75849b",
"c81e728d9d4c2f636f067f89cc14862c",
"eccbc87e4b5ce2fe28308fd9f2a7baf3",
"a87ff679a2f3e71d9181a67b7542122c",
"e4da3b7fbbce2345d7772b0674a318d5",
"1679091c5a880faf6fb5e6087eb1b2dc",
"8f14e45fceea167a5a36dedd4bea2543",
"c9f0f895fb98ab9159f51fd0297e236d",
"45c48cce2e2d7fbdea1afc51c7c6ad26",
"d3d9446802a44259755d38e6d163e820",
"6512bd43d9caa6e02c990b0a82652dca"]


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
    build_num = server.get_job_info(
        CHECK_BUILD_NAME)['lastBuild']['number']
    # retrieve the output of the build (name of build, number of that build)
    output = server.get_build_console_output(CHECK_BUILD_NAME,
        build_num)
    # ensure output contains success and whiteteamKEY
    if (success not in output) or (CHECK_FLAG not in output):
        print("[-] Build failed")
        return False
    # Find the flag in the output
    try:
        flag = re.findall('==== .+', output)[0]
    except:
        flag = "aaaaaaa"
    return incrementShips(ip, flag)


def incrementShips(ip, flag):
    '''Determine the type of ship based on the IP
    Activate on a certain team based on the flag
    '''
    # Determine the team number based on the flag
    try:
        teamNum = HASHES.index(flag[4:].strip())
    except:
        teamNum = ip.split(".")[3]
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
        print("[+] Build ships")
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
