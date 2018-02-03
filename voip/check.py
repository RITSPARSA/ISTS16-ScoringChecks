#!/usr/bin/python
import sys
import os
import pjsua as pj
import time

# usage: scorevoip.py <team>

# Python script that rings the specified extension and returns
# an exit code
# 0 if voip connection successful
# 1 if unsuccessful
#



server_ip = "10.0.2.30"

# Logging callback
def log_cb(level, str, len):
        #print str, # suppressed to prevent spam on command line
        pass

# Callback to receive events from Call
class MyCallCallback(pj.CallCallback):
    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)

    # Notification when call state has changed
    def on_state(self):
        global hit_ringing
        state_text = self.call.info().state_text
        response_code = self.call.info().last_code
        if response_code == 180:
            hit_ringing = True
        elif response_code == 603 or state_text == "DISCONNCTD":
            hit_ringing = False
        elif not response_code == 0 and not response_code == 180 and not response_code == 200:
            hit_ringing = False
        else: 
            print "hit other code"
            hit_ringing = False
        
class MyAccountCallback(pj.AccountCallback):
    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def on_incoming_call(self, call):
        call.hangup(501, "Sorry, not ready to accept calls yet")

    def on_reg_state(self):
        print "Registration complete, status=", self.account.info().reg_status, \
              "(" + self.account.info().reg_reason + ")"
# Check command line argument
if len(sys.argv) != 2:
    print "Usage: scorevoip.py <teamnumber>"
    sys.exit(1)

try:
    # Create library instance
    lib = pj.Lib()

    # Init library with default config
    lib.init(log_cfg = pj.LogConfig(level=0, callback=log_cb))

    # Create UDP transport which listens to any available port
    transport = lib.create_transport(pj.TransportType.UDP)
    
    # Start the library
    lib.start()

    acc_cfg = pj.AccountConfig("10.0.2.30", "3999", "scorethevoip")

    acc_cb = MyAccountCallback()
    acc = lib.create_account(acc_cfg, cb=acc_cb)

    # Make call
    extension=sys.argv[1] # get team number from command line
    uri = "sip:30" + extension + "@" + server_ip # sip uri
    print uri
    if acc.is_valid():
        print "Account is valid and connected"
    else:
        print "Account invalid, not connected"
	print "CANNOT REACH VOIP SERVER"
	sys.exit(0)
    call = acc.make_call(uri, MyCallCallback())
    
    time.sleep(1)
    call.hangup() 
    if hit_ringing:
        print "SUCCESS"
        sys.exit(0) # able to contact phone
    else:
        print "FAILURE"
        sys.exit(0)
    # We're done, shutdown the library
    lib.destroy()

except pj.Error, e:
    lib.destroy()
    lib = None
    print "HIT ERROR"
    sys.exit(1)
