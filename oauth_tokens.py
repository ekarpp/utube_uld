import json
import requests
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import threading
import os


def handler(tokens):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if len(self.path) == 1:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"done")
                tokens.serve = False
            else:
                url = urllib.parse.urlparse(self.address_string() + self.path)
                data = urllib.parse.parse_qs(url.query)

                if "code" not in data:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"code not found in url")
                    tokens.serve = False
                else:
                    tokens.get_tokens(data["code"])
                    self.send_response(301)
                    self.send_header("Location", "http://localhost:8080")
                    self.end_headers()
    return Handler

class Tokens:

    def __init__(self):
        with open("client.json") as f:
            self.client = json.load(f)

        while "tokens.json" not in os.listdir():
            self.create_tokens()
        with open("tokens.json") as f:
            self.tokens = json.load(f)

        return

    # function to get tokens if they dont exist yet
    def get_tokens(self, code):
        r = requests.post("https://oauth2.googleapis.com/token",
                          data = {
                              "client_id": self.client["client_id"],
                              "client_secret": self.client["client_secret"],
                              "code": code,
                              "grant_type": "authorization_code",
                              "redirect_uri": self.client["redirect_uri"]
                          })

        tokens = r.json()
        tokens["expires_in"] += time.time()

        with open("tokens.json", "w") as f:
            json.dump(tokens, f)
        return


    def create_tokens(self):
        URL = "https://accounts.google.com/o/oauth2/v2/auth?"
        URL += urllib.parse.urlencode({
            "client_id": self.client["client_id"],
            "redirect_uri": self.client["redirect_uri"],
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/youtube.upload"
        })
        webbrowser.open(URL)
        server = HTTPServer(('localhost', 8080), handler(self))
        self.serve = True
        while self.serve:
            server.handle_request()
        return

    # function to refresh already existing tokens
    def refresh_tokens(self):
        URL = "https://oauth2.googleapis.com/token"

        body = {
            "client_id": self.client["client_id"],
            "client_secret": self.client["client_secret"],
            "refresh_token": self.tokens["refresh_token"],
            "grant_type": "refresh_token",
        }


        r = requests.post(URL, data = body)
        r = r.json()
        self.tokens["access_token"] = r["access_token"]
        self.tokens["expires_in"] = r["expires_in"] + time.time()

        with open("tokens.json", "w") as f:
            json.dump(self.tokens, f)

        return

    def auth_header(self):
        if self.tokens["expires_in"] < time.time():
            self.refresh_tokens()
        return "Bearer %s" % self.tokens["access_token"]
