'''
    This file is responsible for the authentication server

    All requests must be validated before processing, passing the checks below:
        - Requesting IP address found in whitelist
        - HTTP Request contains the `key` URL keyword argument
            + `key` will be used as the password for the Authentication Database

        - Request Header Includes Values for:
            + `client-id` (Username for Authentication Database)
            + `client-secret` (Compared against recorded API token in Auth DB)

    The Authentication server must ONLY give a response code for the request
        - 200: Success - Credentials have been accepted

        - 401: Unauthorized - Credentials were not provided
        - 403: Forbidden - Provided `client-id` and `key` combination is invalid
        - 406: Not Acceptable - The `client-secret` credential is invalid

        - 418: I'm a teapot - Unable to Handle External Requests
'''

from quart import abort
from quart import request
from quart import Blueprint


whitelist = ['192.168.1.84', '192.168.1.97']


api = Blueprint(__name__)

@api.route('verify?key=<string: key>', methods=['GET', ])
async def verify_key(key: str) -> bool:
    headers = request.headers

    id = headers['client-id']
    secret = headers['client-secret']

    try:
        valid = await ensure_credentials(username=id, pass=key)
    except ValueError:
        return {'status': 'Failed', 'error': 'Invalid Authentication'}, 403

    if secret != valid:
        return {'status': 'Failed', 'error': 'Invalid or Expired Access Token'}, 406

    return {'status': 'OK', 'error': None}, 200

@api.before_serving
async def before_verification():
    if request.headers.get('X-Forwarded-For'):
        try:
            assert request.headers.get('X-Forwarded-For') in whitelist
        except AssertionError:
            return {'status': 'Failed', 'error': 'No coffee here'}, 418

    else:
        try:
            assert request.remote_addr in whitelist
        except AssertionError:
            return {'status': 'Failed', 'error': 'No coffee here'}, 418
