'''
HLS-Proxifier
Copyright 2024 SabBits

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from flask import Flask, request, url_for, Response
from urllib.parse import urljoin, urlparse
import requests
import m3u8
import json

proxy = Flask(__name__)

MAX_RETRIES = 5

def get_base_url(url):
    return urljoin(url, ".")

def is_absolute_url(url):
    parsed_url = urlparse(url)
    return bool(parsed_url.scheme) and bool(parsed_url.netloc)

def configure_single(m3u8_obj, base_url, json_stream_headers):
    for playlist in m3u8_obj.playlists:
        if not is_absolute_url(playlist.uri):
            stream_base = base_url
            is_absolute = False
        else:
            stream_base = None
            is_absolute = True

        playlist.uri = url_for(
            "handle_single", 
            slug=playlist.uri, 
            base=stream_base, 
            absolute=is_absolute, 
            headers=json.dumps(json_stream_headers)
        )

    return m3u8_obj

def configure_segments(m3u8_obj, base_url, json_stream_headers):
    for segment in m3u8_obj.segments:
        if not is_absolute_url(segment.uri):
            single_base = base_url
            is_absolute = False
        else:
            single_base = None
            is_absolute = True

        segment.uri = url_for(
            "handle_ts", 
            slug=segment.uri, 
            base=single_base, 
            absolute=is_absolute, 
            headers=json.dumps(json_stream_headers)
        )

    return m3u8_obj

def configure_keys(m3u8_obj, base_url, json_stream_headers):
    for key in m3u8_obj.keys:
        if key:
            if not is_absolute_url(key.uri):
                single_base = base_url
                is_absolute = False
            else:
                single_base = ""
                is_absolute = True
            key.uri = url_for(
                "handle_key", 
                slug=key.uri,
                base=single_base, 
                absolute=is_absolute, 
                headers=json.dumps(json_stream_headers)
            )

    return m3u8_obj

@proxy.route("/")
def index():
    return "(HLS-Proxifier) is up and running!"

@proxy.route("/proxify")
def hls_proxy():
    stream_url = request.args.get("url")
    stream_headers = request.args.get("headers")

    if stream_headers:
        stream_headers = json.loads(stream_headers)
    else:
        stream_headers = {}
    
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(stream_url, headers=stream_headers)
            response.raise_for_status()
            break
        except:
            continue
    
    m3u8_obj = m3u8.loads(response.text)
    
    if m3u8_obj.is_variant:
        if not len(m3u8_obj.playlists) < 2:
            m3u8_obj = configure_single(m3u8_obj, get_base_url(response.url), stream_headers)
        else:
            uri = m3u8_obj.playlists[0].uri
            segment_response = requests.get(urljoin(get_base_url(response.url), uri), headers=stream_headers)
            m3u8_obj = m3u8.loads(segment_response.text)
            m3u8_obj = configure_segments(m3u8_obj, get_base_url(segment_response.url), stream_headers)
    else:
        m3u8_obj = configure_segments(m3u8_obj, get_base_url(response.url), stream_headers)

    m3u8_obj = configure_keys(m3u8_obj, get_base_url(response.url), stream_headers)
    return Response(m3u8_obj.dumps(), content_type="application/vnd.apple.mpegurl")

@proxy.route("/single")
def handle_single():
    single_slug = request.args.get("slug")
    single_base = request.args.get("base")
    json_single_headers = json.loads(request.args.get("headers"))
    is_absolute = request.args.get("absolute")
    is_absolute = is_absolute.lower() == "true"

    if not is_absolute:
        single_base = single_base
        single_url = urljoin(single_base, single_slug)
    else:
        single_url = single_slug

    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(single_url, headers=json_single_headers)
            response.raise_for_status()
            break
        except:
            continue

    m3u8_obj = m3u8.loads(response.text, uri=get_base_url(single_url))

    m3u8_obj = configure_segments(m3u8_obj, get_base_url(response.url), json_single_headers)
    m3u8_obj = configure_keys(m3u8_obj, get_base_url(response.url), json_single_headers)    

    return Response(m3u8_obj.dumps(), content_type="application/vnd.apple.mpegurl")

@proxy.route("/ts")
def handle_ts():
    ts_slug = request.args.get("slug")
    json_ts_headers = json.loads(request.args.get("headers"))
    ts_base = request.args.get("base")
    is_absolute = request.args.get("absolute")
    is_absolute = is_absolute.lower() == "true"

    if not is_absolute:
        ts_url = urljoin(ts_base, ts_slug)
    else:
        ts_url = ts_slug

    for _ in range(MAX_RETRIES):
        response = requests.get(ts_url, headers=json_ts_headers)
        if response.status_code == 502:
            continue
        break

    return Response(response.content, content_type="application/octet-stream")

@proxy.route("/key")
def handle_key():
    key_slug = request.args.get("slug")
    json_key_headers = json.loads(request.args.get("headers"))
    key_base = request.args.get("base")
    is_absolute = request.args.get("absolute")
    is_absolute = is_absolute.lower() == 'true'

    if not is_absolute:
        key_url = urljoin(key_base, key_slug)
    else:
        key_url = key_slug

    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(key_url, headers=json_key_headers)
            response.raise_for_status()
            break
        except:
            continue
    
    return Response(response.content, content_type="application/octet-stream")

if __name__ == "__main__":
    proxy.run(debug=True)