'''
    File name: AzureChinaCDNPurge.py
    Author: Afa Cheng <afa@afa.moe>
    License: MIT
'''

import urllib
import argparse
import json
import hmac
import hashlib
import sys
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from collections import OrderedDict
from datetime import datetime

def calculate_authorization_header(request_url, request_time, key_id, key_value, http_method):
    urlparts = urllib.parse.urlparse(request_url)
    queries = urllib.parse.parse_qs(urlparts.query)
    ordered_queries = OrderedDict(sorted(queries.items()))
    message = "%s\r\n%s\r\n%s\r\n%s" % (urlparts.path, ", ".join(['%s:%s' % (key, value[0]) for (key, value) in ordered_queries.items()]), request_time, http_method)
    digest = hmac.new(bytearray(key_value, "utf-8"), bytearray(message, "utf-8"), hashlib.sha256).hexdigest().upper()
    return "AzureCDN %s:%s" % (key_id, digest)

def post_purge(path, subscriptionId, endpointId, keyId, keyValue):
    url = f'https://restapi.cdn.azure.cn/subscriptions/{subscriptionId}/endpoints/{endpointId}/purges?apiVersion=1.0'
    data = json.dumps({'Directories': [path]}).encode()
    datestr = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    authHdr = calculate_authorization_header(url, datestr, keyId, keyValue, 'POST')
    headers = { 'content-type': 'application/json', 'x-azurecdn-request-date': datestr, 'Authorization': authHdr }
    req = Request(url, headers=headers, data=data)

    try:
        resp = urlopen(req)
        print('Purging submitted')
        return True
    except HTTPError as e:
        print('Error:')
        print(e.code)
        print(e.read())
        return False
    except URLError as e:
        print("Error: ")
        print(e.reason)
        return False

def main():
    parser = argparse.ArgumentParser(description='Purge Azure China CDN endpoints')
    parser.add_argument('subscriptionId', type=str, help='The subscription ID')
    parser.add_argument('endpointId', type=str, help='The endpoint ID')
    parser.add_argument('path', type=str, help='Purge path')
    parser.add_argument('keyId', type=str, help='API key ID')
    parser.add_argument('keyValue', type=str, help='API key value')

    args = parser.parse_args()

    print(f'Purging "{args.path}" for endpoint {args.endpointId} in {args.subscriptionId}')
    ok = post_purge(args.path, args.subscriptionId, args.endpointId, args.keyId, args.keyValue)

    if ok:
        sys.exit(0)
    else:
        sys.exit(1)

main()
