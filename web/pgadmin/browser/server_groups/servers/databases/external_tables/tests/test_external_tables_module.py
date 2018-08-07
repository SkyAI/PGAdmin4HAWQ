##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import sys

import six

from pgadmin.browser.server_groups.servers\
    .databases.external_tables import ExternalTablesModule
from pgadmin.utils.route import BaseTestGenerator

if sys.version_info < (3, 3):
    from mock import MagicMock, Mock
else:
    from unittest.mock import MagicMock, Mock


class TestExternalTablesModule(BaseTestGenerator):
    scenarios = [
        ('#BackendSupported When access the on a Postgresql Database, '
         'it returns false',
         dict(
             test_type='backend-support',
             manager=dict(
                 server_type='pg',
                 sversion=90100
             ),
             expected_result=False,
         )),
        ('#BackendSupported When access the on a GreenPlum Database, '
         'it returns true',
         dict(
             test_type='backend-support',
             manager=dict(
                 server_type='gpdb',
                 sversion=82303
             ),
             expected_result=True
         )),
        ('#get_nodes when trying to retrieve the node, '
         'it should return true',
         dict(
             test_type='get-nodes',
             function_parameters=dict(
                 gid=10,
                 sid=11,
                 did=12,
             ),
             expected_generate_browser_collection_node_called_with=12
         )),
        ('#get_module_use_template_javascript when checking if need to '
         'generate javascript from template, '
         'it should return false',
         dict(
             test_type='template-javascript',
             expected_result=False
         ))
    ]

    def runTest(self):
        if self.test_type == 'backend-support':
            self.__test_backend_support()
        elif self.test_type == 'get-nodes':
            self.__test_get_nodes()
        elif self.test_type == 'template-javascript':
            self.__test_template_javascript()

    def __test_backend_support(self):
        manager = MagicMock()
        manager.sversion = self.manager['sversion']
        manager.server_type = self.manager['server_type']
        module = ExternalTablesModule('something')
        self.assertEquals(
            self.expected_result,
            module.BackendSupported(manager)
        )

    def __test_get_nodes(self):
        module = ExternalTablesModule('something')
        module.generate_browser_collection_node = Mock()

        result = module.get_nodes(**self.function_parameters)
        six.next(result)

        module.generate_browser_collection_node.assert_called_with(
            self.expected_generate_browser_collection_node_called_with
        )

    def __test_template_javascript(self):
        module = ExternalTablesModule('something')
        self.assertEquals(
            self.expected_result,
            module.module_use_template_javascript)
