"""
Scoring check for Ecomm app
"""
import argparse
import requests

AUTH_API_URL = "http://10.0.20.21:9000"
BANK_API_URL = "http://10.0.20.21:5000"

SCORING_USER = "doshmajhan"
SCORING_PASSWORD = "anotherdayanotherdollar23$"


def api_request(endpoint, data, url, sess):
    """
    Makes a request to our api and returns the response

    :param endpoint: the api endpoint to hit
    :param data: the data to send in dictionary format
    :param url: the url to send the data to
    :param sess: requests sess

    :returns resp: the api response
    """
    url = "{}/{}".format(url, endpoint)

    resp = sess.post(url, data=data)

    if resp.status_code == 400:
        print resp.json()
        raise Exception("Bad request sent to API")

    if resp.status_code == 403:
        raise Exception(resp.json()['error'])

    elif resp.status_code != 200:
        raise Exception("App returned {} for /{}".format(resp.status_code, endpoint))

    return resp

def get_token_from_whiteteam(sess):
    """
    Gets an auth token for our white team account from the auth api

    :param address: the address of their ecomm app
    :param sess: requests session
    :returns token: the auth token for white team account
    """
    data = dict()
    data['username'] = SCORING_USER
    data['password'] = SCORING_PASSWORD
    endpoint = 'login'
    resp = api_request(endpoint, data, AUTH_API_URL, sess)
    if 'token' not in resp.json():
        raise Exception('No token in Ecomm login response')

    return resp.json()['token']

def check(team, address):
    """
    Runs a check to buy an item on a teams store, and then will give that team money if it works

    :param team: the team num to check
    :param address: the address of their ecommerce box
    """
    sess = requests.Session()

    # log into their app
    data = dict()
    data['username'] = SCORING_USER
    data['password'] = SCORING_PASSWORD
    endpoint = 'login'
    resp = api_request(endpoint, data, address, sess)

    # try to buy an item
    post_data = dict()
    post_data['item_id'] = 3
    endpoint = 'shop'
    resp = api_request(endpoint, post_data, address, sess)
    if "Insufficient funds" not in resp.content:
        raise Exception("Failed")

    # transfer money to team since it passed
    token = get_token_from_whiteteam(sess)
    post_data = dict()
    post_data['token'] = token
    post_data['team_id'] = team
    post_data['amount'] = 10000
    resp = api_request('dosh-add-credits', post_data, BANK_API_URL, sess)
    if 'success' in resp.json():
        print "SUCCESS"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check a teams web app")
    parser.add_argument('-t', dest='team', help='team number')
    parser.add_argument('-a', dest='address', help='ecommerce url (include http://)')

    args = parser.parse_args()
    team = args.team
    address = args.address

    check(team, address)
