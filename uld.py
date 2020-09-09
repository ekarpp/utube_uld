#!/usr/bin/env python3
import os
import requests
import oauth_tokens
import argparse
import json
import mimetypes

from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField



'''
makes a multipart/related HTTP request body
parts is an array containing dictionaries
each dictionary contains a description for a HTTP request
required dictionary fields are: name, headers and data
'''
def make_multipart(parts):
    fields = [RequestField(name=part.name, headers=part.headers, data=part.data) for part in parts]
    bound = choose_boundary()
    data, _ = encode_multipart_formdata([f1, f2], bound)
    content_type = "multipart/related; boundary=%s" % bound

    return data, content_type


# main upload function
def upld(video, token):
    URL = "https://www.googleapis.com/upload/youtube/v3/videos"

    headers = {
        "Authorization": token
    }

    js = {
        "snippet": {
            "title": video.title,
            "description": video.description,
            "categoryId": video.category
        },
        "status": {
            "privacyStatus": "private"
        }
    }

    MIME = mimetypes.guess_type(video.path)[0]
    if MIME is None or MIME.split("/")[0] != "video":
        print("ERROR")
        return

    with open(video.path, "rb") as f:
        parts = [
            {"name": "json", "headers": {"Content-Type": "application/json"}, "data": json.dumps(js)},
            {"name": "video", "headers": {"Content-Type": MIME, "Content-Transfer-Encoding": "binary"}, "data": f.read()}
        ]
        data, content_type = make_multipart(parts)

        headers["Content-Type"] = content_type
        #URL = "http://httpbin.org/post"
        params = {"part": "snippet,status", "uploadType": "multipart"}
        r = requests.post(URL, data = data, headers = headers, params = params)
        print(r)
        print(r.text)
        #req = requests.Request("POST", URL, headers = headers, data = data)
        #prep = req.prepare()
        #print('\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()))
        #print()
        #print(prep.body)
    return

def main():
    parser = argparse.ArgumentParser(prog="uld", description="Uploads youtube videoust")
    parser.add_argument("path", help="videoust path")
    parser.add_argument("-c", help="videoust category", dest="category", required=True)
    parser.add_argument("-t", help="title", dest="title", required=True)
    parser.add_argument("-d", help="description", dest="description", required=True)
    vid = parser.parse_args()

    if not os.path.isfile(vid.path):
        print("ERROR")
        return

    tokens = oauth_tokens.Tokens()
    upld(vid, tokens.auth_header())

main()
