#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import json
import readline  # noqa
import sys

SESSION_ID_HEADER_NAME = 'X-Transmission-Session-Id'
RPC_DEFAULT_HOST = '127.0.0.1'
RPC_DEFAULT_PORT = '9091'

try:
    # Python 3
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    # Python 2
    from urllib2 import urlopen, HTTPError, Request, URLError

try:
    # Python 2
    input = raw_input
except NameError:
    # Python 3
    pass

if sys.version_info < (3,):
    # Python 2
    def ustring(string):
        return string.encode('utf-8')
else:
    # Python 3
    def ustring(string):
        return string


def get_rpc_url(host=None, port=None):
    return 'http://{0}:{1}/transmission/rpc'.format(
        host or RPC_DEFAULT_HOST,
        port or RPC_DEFAULT_PORT
    )

session_id = None

rpc_url = get_rpc_url()

print('Default Transmission RPC URL is "{0}"'.format(rpc_url))

new_rpc_host = input('Press enter to use "{0}" as RPC host, or type another one: '.format(RPC_DEFAULT_HOST))
new_rpc_port = input('Press enter to use "{0}" as RPC port, or type another one: '.format(RPC_DEFAULT_PORT))

if new_rpc_host or new_rpc_port:
    rpc_url = get_rpc_url(new_rpc_host, new_rpc_host)
    print('Using "{0}" instead'.format(rpc_url))

look_for_string = input('Enter the string in the announce URL that you want to replace: ')

if not look_for_string:
    sys.exit('You must enter a string to replace')

replace_with_string = input('Enter the new string you want to replace it with: ')

if not replace_with_string:
    sys.exit('You must enter a new string to replace the old one')


def call_rpc(method=None, arguments=None):
    global session_id

    request = Request(rpc_url)

    if session_id:
        request.add_header(SESSION_ID_HEADER_NAME, session_id)

    if method:
        payload = {'method': method}
        if arguments:
            payload['arguments'] = arguments
        json_data = json.dumps(payload)
        request.data = json_data.encode('utf-8')

    response = None

    try:
        response = urlopen(request)
    except HTTPError as e:
        # The first request will return a 409 status that includes a session id
        # we need to include in the header of all subsequent requests. So get it
        # from the 409 response and save it.
        if e.code == 409:
            session_id = e.headers[SESSION_ID_HEADER_NAME]
            response = call_rpc(method, arguments)
        else:
            sys.exit('Got an unexpected response from RPC: {0} {1}, aborting.'.format(e.code, e.message))
    except URLError as e:
        sys.exit('Could not connect to Transmission. Is it running and allows remote access? {0}'.format(e.reason))

    return response

response = call_rpc('torrent-get', {
    'fields': ['id', 'name', 'trackers']
})
response = response.read()
response = response.decode('utf-8')

data = json.loads(response)

if 'arguments' not in data:
    sys.exit('Got no arguments from RPC response.')

if 'torrents' not in data['arguments']:
    sys.exit('Found no active torrents.')

torrents = data['arguments']['torrents']

print('Found {0} torrents'.format(len(torrents)))

count = 0

for torrent in torrents:
    print('Checking torrent "{0!s}"'.format(ustring(torrent['name'])))
    for tracker in torrent['trackers']:
        old_announce = tracker['announce']
        if look_for_string in old_announce:
            print('Found "{0}" in tracker, replacing it with "{1}".'.format(look_for_string, replace_with_string))
            new_announce = old_announce.replace(look_for_string, replace_with_string)
            response = call_rpc('torrent-set', {
                'ids': [torrent['id']],
                'trackerReplace': [tracker['id'], new_announce]
            })
            count += 1

print('Done! Replaced {0} occurrences of "{1}" with "{2}"'.format(count, look_for_string, replace_with_string))
