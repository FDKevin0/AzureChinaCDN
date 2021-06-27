import urllib
import hmac
import hashlib
from collections import OrderedDict

def calculate_authorization_header(request_url, request_time, key_id, key_value, http_method):
    """ Calculate the authorization header.
    @request_url: Complete request URL with scheme, host, path and queries
    @request_time: UTC request time with format yyyy-MM-dd HH:mm:ss
    @key_id: API key ID
    @key_value: API key value
    @http_method: Http method in upper case
    """
    
    urlparts = urllib.parse.urlparse(request_url)
    queries = urllib.parse.parse_qs(urlparts.query)
    ordered_queries = OrderedDict(sorted(queries.items()))
    message = "%s\r\n%s\r\n%s\r\n%s" % (urlparts.path, ", ".join(['%s:%s' % (key, value[0]) for (key, value) in ordered_queries.items()]), request_time, http_method)
    digest = hmac.new(bytearray(key_value, "utf-8"), bytearray(message, "utf-8"), hashlib.sha256).hexdigest().upper()
    return "AzureCDN %s:%s" % (key_id, digest)