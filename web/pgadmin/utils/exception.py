##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
from flask_babelex import gettext as _
from flask import request

from pgadmin.utils.ajax import service_unavailable


class ConnectionLost(HTTPException):
    """
    Exception
    """

    def __init__(self, _server_id, _database_name, _conn_id):
        self.sid = _server_id
        self.db = _database_name
        self.conn_id = _conn_id
        HTTPException.__init__(self)

    @property
    def name(self):
        return HTTP_STATUS_CODES.get(503, 'Service Unavailable')

    def get_response(self, environ=None):
        return service_unavailable(
            _("Connection to the server has been lost."),
            info="CONNECTION_LOST",
            data={
                'sid': self.sid,
                'database': self.db,
                'conn_id': self.conn_id
            }
        )

    def __str__(self):
        return "Connection (id #{2}) lost for the server (#{0}) on " \
               "database ({1})".format(self.sid, self.db, self.conn_id)

    def __repr__(self):
        return "Connection (id #{2}) lost for the server (#{0}) on " \
               "database ({1})".format(self.sid, self.db, self.conn_id)


class SSHTunnelConnectionLost(HTTPException):
    """
    Exception when connection to SSH tunnel is lost
    """

    def __init__(self, _tunnel_host):
        self.tunnel_host = _tunnel_host
        HTTPException.__init__(self)

    @property
    def name(self):
        return HTTP_STATUS_CODES.get(503, 'Service Unavailable')

    def get_response(self, environ=None):
        return service_unavailable(
            _("Connection to the SSH Tunnel for host '{0}' has been lost. "
              "Reconnect to the database server.").format(self.tunnel_host),
            info="SSH_TUNNEL_CONNECTION_LOST",
            data={
                'tunnel_host': self.tunnel_host
            }
        )

    def __str__(self):
        return "Connection to the SSH Tunnel for host '{0}' has been lost. " \
               "Reconnect to the database server".format(self.tunnel_host)

    def __repr__(self):
        return "Connection to the SSH Tunnel for host '{0}' has been lost. " \
               "Reconnect to the database server".format(self.tunnel_host)
