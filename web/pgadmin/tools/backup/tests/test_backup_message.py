##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import sys

from pgadmin.tools.backup import BackupMessage, BACKUP
from pgadmin.utils.route import BaseTestGenerator

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch


class BackupMessageTest(BaseTestGenerator):
    """Test the BackupMessage class"""
    scenarios = [
        ('When Backup server',
         dict(
             class_params=dict(
                 type=BACKUP.SERVER,
                 sid=1,
                 name='test_backup_server',
                 port=5444,
                 host='localhost',
                 database='postgres',
                 bfile='test_restore',
                 args=[
                     '--file',
                     "backup_file",
                     '--host',
                     "localhost",
                     '--port',
                     "5444",
                     '--username',
                     "postgres",
                     '--no-password',
                     '--database',
                     "postgres"
                 ],
                 cmd="/test_path/pg_dump"
             ),
             extected_msg="Backing up the server"
                          " 'test_backup_server (localhost:5444)'...",
             expetced_details_cmd='/test_path/pg_dump --file '
                                  '"backup_file" --host "localhost" '
                                  '--port "5444" --username "postgres" '
                                  '--no-password --database "postgres"'

         )),
        ('When Backup global',
         dict(
             class_params=dict(
                 type=BACKUP.GLOBALS,
                 sid=1,
                 name='test_backup_server',
                 port=5444,
                 host='localhost',
                 database='postgres',
                 bfile='test_backup',
                 args=[
                     '--file',
                     'backup_file',
                     '--host',
                     'localhost',
                     '--port',
                     '5444',
                     '--username',
                     'postgres',
                     '--no-password',
                     '--database',
                     'postgres'
                 ],
                 cmd="/test_path/pg_dump"
             ),
             extected_msg="Backing up the global objects on the server "
                          "'test_backup_server (localhost:5444)'...",
             expetced_details_cmd='/test_path/pg_dump --file "backup_file" '
                                  '--host "localhost"'
                                  ' --port "5444" --username "postgres" '
                                  '--no-password --database "postgres"'

         )),
        ('When backup object',
         dict(
             class_params=dict(
                 type=BACKUP.OBJECT,
                 sid=1,
                 name='test_backup_server',
                 port=5444,
                 host='localhost',
                 database='postgres',
                 bfile='test_backup',
                 args=[
                     '--file',
                     'backup_file',
                     '--host',
                     'localhost',
                     '--port',
                     '5444',
                     '--username',
                     'postgres',
                     '--no-password',
                     '--database',
                     'postgres'
                 ],
                 cmd="/test_path/pg_dump"
             ),
             extected_msg="Backing up an object on the server "
                          "'test_backup_server (localhost:5444)'"
                          " from database 'postgres'...",
             expetced_details_cmd='/test_path/pg_dump --file "backup_file" '
                                  '--host "localhost" '
                                  '--port "5444" --username "postgres" '
                                  '--no-password --database "postgres"'

         ))
    ]

    @patch('pgadmin.tools.backup.BackupMessage.get_server_details')
    def runTest(self, get_server_details_mock):
        get_server_details_mock.return_value = \
            self.class_params['name'],\
            self.class_params['host'],\
            self.class_params['port']

        backup_obj = BackupMessage(
            self.class_params['type'],
            self.class_params['sid'],
            self.class_params['bfile'],
            *self.class_params['args'],
            **{'database': self.class_params['database']}
        )

        # Check the expected message returned
        self.assertEqual(backup_obj.message, self.extected_msg)

        # Check the command
        obj_details = backup_obj.details(self.class_params['cmd'],
                                         self.class_params['args'])
        self.assertIn(self.expetced_details_cmd, obj_details)
