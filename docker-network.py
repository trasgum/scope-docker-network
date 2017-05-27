#!/usr/bin/env python

from docker import Client
import BaseHTTPServer
import SocketServer
import datetime
import errno
import json
import os
import signal
import socket
import threading
import time
import urllib2

PLUGIN_ID="docker-network"
PLUGIN_UNIX_SOCK="/var/run/scope/plugins/" + PLUGIN_ID + ".sock"
DOCKER_SOCK="unix://var/run/docker.sock"

nodes = {}

def update_loop():
    global nodes
    next_call = time.time()
    while True:
        # Get current timestamp in RFC3339
        timestamp = datetime.datetime.utcnow()
        timestamp = timestamp.isoformat('T') + 'Z'

        # Fetch and convert data to scope data model
        new = {}
        for container_id, network in container_attached_network().iteritems():
            new["%s;<container>".format(container_id)] = {
                'latest': {
                    'network': {
                        'timestamp': timestamp,
                        'value': str(network),
                    }
                }
            }

        nodes = new
        next_call += 5
        time.sleep(next_call - time.time())


def start_update_loop():
    updateThread = threading.Thread(target=update_loop)
    updateThread.daemon = True
    updateThread.start()


def container_attached_network():
    containers = dict()
    cli = Client(base_url=DOCKER_SOCK, version='auto')
    for c in cli.containers(all=True):
        containers[c['Id']] = c['NetworkSettings']['Networks'].keys()[0]
    return containers


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        # The logger requires a client_address, but unix sockets don't have
        # one, so we fake it.
        self.client_address = "-"

        # Generate our json body
        body = json.dumps({
            'Plugins': [
                {
                    'id': PLUGIN_ID,
                    'label': 'docker network',
                    'description': 'Shows which network container is attached',
                    'interfaces': ['reporter'],
                    'api_version': '1',
                }
            ],
            'Container': {
                'nodes': nodes,
                # Templates tell the UI how to render this field.
                'metadata_templates': {
                    'network': {
                        # Key where this data can be found.
                        'id': "docker_network",
                        # Human-friendly field name
                        'label': "Network",
                        # Look up the 'id' in the latest object.
                        'from': "latest",
                        # Priorities over 10 are hidden, lower is earlier in the list.
                        'priority': 0.1,
                    },
                },
            },
        })

        # Send the headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()

        # Send the body
        self.wfile.write(body)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def delete_socket_file():
    if os.path.exists(PLUGIN_UNIX_SOCK):
        os.remove(PLUGIN_UNIX_SOCK)

def sig_handler(b, a):
    delete_socket_file()
    exit(0)


def main():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    start_update_loop()

    # Ensure the socket directory exists
    mkdir_p(os.path.dirname(PLUGIN_UNIX_SOCK))
    # Remove existing socket in case it was left behind
    delete_socket_file()
    # Listen for connections on the unix socket
    server = SocketServer.UnixStreamServer(PLUGIN_UNIX_SOCK, Handler)
    try:
        server.serve_forever()
    except:
        delete_socket_file()
        raise

main()
