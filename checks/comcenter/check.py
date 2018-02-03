"""
Scoring check for Command Center app
"""
import argparse
import requests


def check(address):
    """
    Runs a check to buy an item on a teams store, and then will give that team money if it works

    :param team: the team num to check
    :param address: the address of their ecommerce box
    """
    resp = requests.get(address)
    if resp.status_code == 200:
        print "SUCCESS"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Check a teams web app")
    parser.add_argument('-a', dest='address', help='command center url (include http://)')

    args = parser.parse_args()
    address = args.address

    check(address)
