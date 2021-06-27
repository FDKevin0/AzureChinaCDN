import argparse
import json
import sys
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from datetime import datetime
from request import calculate_authorization_header


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
