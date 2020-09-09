#!/usr/bin/env python3
import os
import requests
import oauth_tokens
import argparse
import json
import mimetypes

# todo: write own
from urllib3.filepost import choose_boundary



'''
makes a multipart/related HTTP request body
parts is an array containing dictionaries
each dictionary contains a description for a HTTP request
required dictionary fields are: headers and data
data must be in binary form
'''
def make_multipart(parts):
    bound = choose_boundary()
    content_type = "multipart/related; boundary=%s" % bound

    bound = ("\n--" + bound).encode()
    # data is the whole body
    data = bound[1:]
    for part in parts:
        # and rq is the body for each part
        rq = "\n"
        for header in part["headers"]:
            rq += f"{header}: {part['headers'][header]}\n"
        rq += "\n"
        try:
            data += rq.encode() + part["data"] + bound
        except TypeError:
            print("Data was not bytes")
    data += b"--\n"
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
            {"name": "json", "headers": {"Content-Type": "application/json"}, "data": json.dumps(js).encode()},
            {"name": "video", "headers": {"Content-Type": MIME, "Content-Transfer-Encoding": "binary"}, "data": f.read()}
        ]
        data, content_type = make_multipart(parts)

        headers["Content-Type"] = content_type
        params = {"part": "snippet,status", "uploadType": "multipart"}
        r = requests.post(URL, data = data, headers = headers, params = params)
        print(r)
        print(r.text)
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
