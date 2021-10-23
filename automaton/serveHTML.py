"""
Serve local HTML files with python simple server

See https://stackabuse.com/serving-files-with-pythons-simplehttpserver-module/

Optionally establish Ngrok tunnel with pyngrok, see https://pyngrok.readthedocs.io/en/latest/integrations.html#python-http-server

23/10/21

"""
import os
from pathlib import Path

import functools
import http.server
import socketserver

from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    from pyngrok import ngrok
    pyngrokFlag = True

except ImportError as e:
    print(f"Failed to import pyngrok, tunnels not available.")
    pyngrokFlag = False

def initNgrok(port):
    """
    Init Ngrok tunnel.

    See https://pyngrok.readthedocs.io/en/latest/integrations.html#python-http-server
    """

    public_url = ngrok.connect(port).public_url
    print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    return public_url



def serveDir(port = 6709, htmlDir = None, public_url=None):
    """
    Serve directory with python simple server.

    Optionally create Ngrok tunnel if pyngrok installed.
    See https://pyngrok.readthedocs.io/en/latest/integrations.html#python-http-server

    Note: dir handling, see https://stackoverflow.com/questions/39801718/how-to-run-a-http-server-which-serves-a-specific-path
    """

    port = os.environ.get("PORT", port)

    if htmlDir is None:
        htmlDir = os.getcwd()

    # Use pyngork? If pulic_url is set use it, otherwise init new tunnel
    if pyngrokFlag:
        if public_url is None:
            public_url = initNgrok(port)

#         print("Ngrok URL: \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))


    server_address = ("", port)
#     handler = http.server.SimpleHTTPRequestHandler  #(directory = htmlDir)  # Can't specify dir only here?

    # With dir handling, see https://stackoverflow.com/a/58217918
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=htmlDir)

    # Try/except style

    # httpd = HTTPServer(server_address, BaseHTTPRequestHandler)
#     httpd = socketserver.TCPServer(server_address, handler)  #(directory = htmlDir))
#     try:
#         # Block until CTRL-C or some other terminating event
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#        print(" Shutting down server.")

#        httpd.socket.close()

    # Context manager style
    with socketserver.TCPServer(server_address, handler) as httpd:
#         print("Serving at port", port)
        if pyngrokFlag:
            print("Serving: \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))
        else:
            print("Serving: \"http://127.0.0.1:{}\"".format(port))

        httpd.serve_forever()