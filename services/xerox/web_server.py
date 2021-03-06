# -*- coding: utf-8 -*-
"""Xerox web server module."""
from __future__ import unicode_literals

import os
import threading

try:
    from socketserver import ThreadingMixIn  # Python 3 exclusive
    from http.server import HTTPServer, SimpleHTTPRequestHandler
except Exception:
    from SocketServer import ThreadingMixIn  # Python 2 exclusive
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler

from common_strings import STARTUP_MSG, SHUTDOWN_MSG, ERROR_MSG

WEB_PORT = 80
WWW_FOLDER_NAME = "www"
WEB_ALERT_TYPE_NAME = "xerox_web_interaction"
DEFAULT_SERVER_VERSION = "nginx"
SERVER_NAME = "Xerox Web Server"
ALERTS = [WEB_ALERT_TYPE_NAME]


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Threading HTTP Server stub class."""


class HoneyHTTPRequestHandler(SimpleHTTPRequestHandler, object):
    """HTTP Request Handler."""

    def version_string(self):
        """HTTP Server version header."""
        return DEFAULT_SERVER_VERSION

    def send_head(self):
        """Handle every request by raising an alert."""
        self.alert_callback(event_name=WEB_ALERT_TYPE_NAME,
                            request=" ".join([self.command, self.path]),
                            orig_ip=self.client_address[0],
                            orig_port=self.client_address[1])
        return super(HoneyHTTPRequestHandler, self).send_head()

    def log_request(self, code="-", size="-"):
        """Log request."""
        self.debug_callback("debug: {request}, code: {code}, size: {size}".format(request=self.requestline,
                                                                                  code=code,
                                                                                  size=size))

    def log_error(self, *args):
        """Log an error."""
        self.debug_callback("error: {message} ({args})".format(message=args[0], args=args))


class XeroxWebServer(object):
    """Xerox Web Server."""

    def __init__(self, alert_callback, logger):
        self.thread = None
        alerting_client_handler = HoneyHTTPRequestHandler
        alerting_client_handler.debug_callback = logger.debug
        alerting_client_handler.info_callback = logger.info
        alerting_client_handler.alert_callback = alert_callback
        self.httpd = ThreadingHTTPServer(("", WEB_PORT), alerting_client_handler)

    def start(self):
        """Start server."""
        os.chdir(os.path.join(os.path.dirname(__file__), WWW_FOLDER_NAME))
        self.logger.info(STARTUP_MSG.format(name=SERVER_NAME, port=WEB_PORT))
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        try:
            self.thread.start()
        except Exception as err:
            self.debug(ERROR_MSG.format(error=err))
            return False

        return True

    def stop(self):
        """Stop server."""
        self.logger.info(SHUTDOWN_MSG.format(name=SERVER_NAME))
        if self.httpd:
            self.httpd.shutdown()
            self.httpd = None

    def __str__(self):
        return SERVER_NAME
