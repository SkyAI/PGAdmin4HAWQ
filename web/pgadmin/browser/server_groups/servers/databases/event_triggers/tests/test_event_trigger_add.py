##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import json
import uuid

from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.browser.server_groups.servers.databases.tests import \
    utils as database_utils
from pgadmin.utils import server_utils as server_utils
from pgadmin.utils.route import BaseTestGenerator
from regression import parent_node_dict
from regression import trigger_funcs_utils
from regression.python_test_utils import test_utils as utils


class EventTriggerAddTestCase(BaseTestGenerator):
    """ This class will add new event trigger under test schema. """
    scenarios = [
        # Fetching default URL for event trigger node.
        ('Fetch Event Trigger Node URL',
         dict(url='/browser/event_trigger/obj/'))
    ]

    def setUp(self):
        self.schema_data = parent_node_dict['schema'][-1]
        self.server_id = self.schema_data['server_id']
        self.db_id = self.schema_data['db_id']
        self.schema_name = self.schema_data['schema_name']
        self.schema_id = self.schema_data['schema_id']
        self.extension_name = "postgres_fdw"
        self.db_name = parent_node_dict["database"][-1]["db_name"]
        self.func_name = "trigger_func_%s" % str(uuid.uuid4())[1:8]
        self.db_user = self.server["username"]
        server_con = server_utils.connect_server(self, self.server_id)
        if not server_con["info"] == "Server connected.":
            raise Exception("Could not connect to server to add resource "
                            "groups.")
        server_version = 0
        if "type" in server_con["data"]:
            if server_con["data"]["version"] < 90300:
                message = "Event triggers are not supported by PG9.2 " \
                          "and PPAS9.2 and below."
                self.skipTest(message)
        self.function_info = trigger_funcs_utils.create_trigger_function(
            self.server, self.db_name, self.schema_name, self.func_name,
            server_version)

    def runTest(self):
        """ This function will add event trigger under test database. """
        db_con = database_utils.connect_database(self, utils.SERVER_GROUP,
                                                 self.server_id, self.db_id)
        if not db_con['data']["connected"]:
            raise Exception("Could not connect to database.")
        schema_response = schema_utils.verify_schemas(self.server,
                                                      self.db_name,
                                                      self.schema_name)
        if not schema_response:
            raise Exception("Could not find the schema.")
        func_name = self.function_info[1]
        func_response = trigger_funcs_utils.verify_trigger_function(
            self.server,
            self.db_name,
            func_name)
        if not func_response:
            raise Exception("Could not find the trigger function.")
        data = {
            "enabled": "O",
            "eventfunname": "%s.%s" % (self.schema_name, self.func_name),
            "eventname": "DDL_COMMAND_END",
            "eventowner": self.db_user,
            "name": "event_trigger_add_%s" % (str(uuid.uuid4())[1:8]),
            "providers": []
        }
        response = self.tester.post(
            self.url + str(utils.SERVER_GROUP) + '/' +
            str(self.server_id) + '/' + str(self.db_id) +
            '/', data=json.dumps(data),
            content_type='html/json')
        self.assertAlmostEquals(response.status_code, 200)

    def tearDown(self):
        # Disconnect database
        database_utils.disconnect_database(self, self.server_id, self.db_id)
