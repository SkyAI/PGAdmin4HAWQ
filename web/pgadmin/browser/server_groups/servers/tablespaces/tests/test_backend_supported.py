##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################
import sys

if sys.version_info < (3, 3):
    from mock import MagicMock
else:
    from unittest.mock import MagicMock

from pgadmin.browser.server_groups.servers.tablespaces import TablespaceModule
from pgadmin.utils.route import BaseTestGenerator


class BackendSupportedTestCase(BaseTestGenerator):
    """This class will add tablespace node under server"""
    scenarios = [
        ('When server is postgres, it returns true',
         dict(
             manager=dict(
                 sversion=90100,
                 server_type='pg'
             ),
             expected_result=True
         )),
        ('When server is GreenPlum 5.0, it returns false',
         dict(
             manager=dict(
                 sversion=80323,
                 server_type='gpdb'
             ),
             expected_result=False
         ))
    ]

    class LocalManager:
        def __init__(self, properties):
            self.sversion = properties['sversion']
            self.sversion = properties['sversion']

    def runTest(self):
        module = TablespaceModule('name')
        manager = MagicMock()
        manager.sversion = self.manager['sversion']
        manager.server_type = self.manager['server_type']
        self.assertEquals(
            self.expected_result, module.BackendSupported(manager)
        )
