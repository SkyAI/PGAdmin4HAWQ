##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import sys

from pgadmin.misc.bgprocess.processes import BatchProcess, IProcessDesc
from pgadmin.tools.backup import BackupMessage, BACKUP
from pgadmin.utils.route import BaseTestGenerator
from pickle import dumps, loads

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch


class BatchProcessTest(BaseTestGenerator):
    """Test the BatchProcess class"""
    scenarios = [
        ('When backup server',
         dict(
             class_params=dict(
                 type=BACKUP.SERVER,
                 sid=1,
                 name='test_backup_server',
                 port=5444,
                 host='localhost',
                 database='postgres',
                 username='postgres',
                 bfile='test_backup',
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
                 cmd='backup_server'
             )
         )),
        ('When backup globals',
         dict(
             class_params=dict(
                 type=BACKUP.GLOBALS,
                 sid=1,
                 name='test_backup_server',
                 port=5444,
                 host='localhost',
                 database='postgres',
                 username='postgres',
                 bfile='test_backup',
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
                 cmd='backup'
             )
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
                 username='postgres',
                 bfile='test_backup',
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
                 cmd='backup'
             )
         ))
    ]

    @patch('pgadmin.tools.backup.BackupMessage.get_server_details')
    @patch('pgadmin.misc.bgprocess.processes.Popen')
    @patch('pgadmin.misc.bgprocess.processes.current_app')
    @patch('pgadmin.misc.bgprocess.processes.db')
    @patch('pgadmin.tools.backup.current_user')
    @patch('pgadmin.misc.bgprocess.processes.current_user')
    def runTest(self, current_user_mock, current_user, db_mock,
                current_app_mock, popen_mock, get_server_details_mock):
        current_user.id = 1
        current_user_mock.id = 1
        current_app_mock.PGADMIN_RUNTIME = False

        def db_session_add_mock(j):
            if sys.version_info < (2, 7):
                cmd_obj = loads(str(j.desc))
            else:
                cmd_obj = loads(j.desc)
            self.assertTrue(isinstance(cmd_obj, IProcessDesc))
            self.assertEqual(cmd_obj.backup_type, self.class_params['type'])
            self.assertEqual(cmd_obj.bfile, self.class_params['bfile'])
            self.assertEqual(cmd_obj.database, self.class_params['database'])
            self.assertEqual(cmd_obj.cmd,
                             ' --file "backup_file" '
                             '--host "{0}" '
                             '--port "{1}" '
                             '--username "{2}" '
                             '--no-password '
                             '--database "{3}"'.format(
                                 self.class_params['host'],
                                 self.class_params['port'],
                                 self.class_params['username'],
                                 self.class_params['database']
                             ))

        db_mock.session.add.side_effect = db_session_add_mock

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

        p = BatchProcess(
            desc=backup_obj,
            cmd=self.class_params['cmd'],
            args=self.class_params['args']
        )

        # Check that _create_process has been called
        self.assertTrue(db_mock.session.add.called)

        # Check start method
        self._check_start(popen_mock, p)

        # Check list method
        self._check_list(p, backup_obj)

    def _check_start(self, popen_mock, p):
        cmd_test = self.class_params['cmd']
        assert_true = self.assertTrue

        class popenMockSideEffect():
            def __init__(self, cmd, **kwargs):
                assert_true(cmd_test in cmd)
                assert_true('env' in kwargs)

            def poll(self):
                pass

        popen_mock.side_effect = popenMockSideEffect
        p.start()

        self.assertTrue(popen_mock.called)

    @patch('pgadmin.misc.bgprocess.processes.Process')
    @patch('pgadmin.misc.bgprocess.processes.BatchProcess.'
           'update_process_info')
    def _check_list(self, p, backup_obj, update_process_info_mock,
                    process_mock):
        class TestMockProcess():
            def __init__(self, desc, args, cmd):
                self.pid = 1
                self.exit_code = 1
                self.start_time = '2018-04-17 06:18:56.315445 +0000'
                self.end_time = None
                self.desc = dumps(desc)
                self.arguments = " ".join(args)
                self.command = cmd
                self.acknowledge = None

        process_mock.query.filter_by.return_value = [
            TestMockProcess(backup_obj,
                            self.class_params['args'],
                            self.class_params['cmd'])]

        update_process_info_mock.return_value = [True, True]

        ret_value = p.list()
        self.assertEqual(1, len(ret_value))
        self.assertTrue('details' in ret_value[0])
        self.assertTrue('desc' in ret_value[0])
