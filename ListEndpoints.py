import argparse
import sys
import json
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from datetime import datetime
from request import calculate_authorization_header


def list_endpoints(subscriptionId, keyId, keyValue):
    url = f'https://restapi.cdn.azure.cn/subscriptions/{subscriptionId}/endpoints?apiVersion=1.0'
    datestr = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    authHdr = calculate_authorization_header(url, datestr, keyId, keyValue, 'GET')
    headers = { 'content-type': 'application/json', 'x-azurecdn-request-date': datestr, 'Authorization': authHdr }
    req = Request(url, headers=headers)

    try:
        resp = urlopen(req)
        print('Listing Endpoints')
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
    finally :
        data = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description='List Azure China CDN endpoints')
    parser.add_argument('subscriptionId', type=str, help='The subscription ID')
    parser.add_argument('keyId', type=str, help='API key ID')
    parser.add_argument('keyValue', type=str, help='API key value')

    args = parser.parse_args()

    ok = list_endpoints(args.subscriptionId, args.keyId, args.keyValue)

    if ok:
        sys.exit(0)
    else:
        sys.exit(1)

main()
