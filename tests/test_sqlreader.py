from tests.compat import AsyncTestCase, AsyncMock, MagicMock, patch
import unittest.mock as mock
from spade_artifact.common.readers.sqlreader import DatabaseQueryArtifact

class TestDatabaseQueryArtifact(AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.connection_params = {'host': 'localhost', 'user': 'test', 'password': 'test', 'database': 'testdb'}
        self.query = "SELECT * FROM test_table"
        self.mock_db_connection = MagicMock()

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.connection_params = {'host': 'localhost', 'user': 'test', 'password': 'test', 'database': 'testdb'}
        self.query = "SELECT * FROM test_table"
        self.mock_db_connection = MagicMock()

    def test_connection_parameters_validation_postgresql(self):
        with self.assertRaises(ValueError):
            artifact = DatabaseQueryArtifact("jid@test.com", "password", "postgresql", {},
                                           query=self.query)
            artifact.validate_connection_params()

    def test_connection_parameters_validation_mysql(self):
        with self.assertRaises(ValueError):
            artifact = DatabaseQueryArtifact("jid@test.com", "password", "mysql", {},
                                           query=self.query)
            artifact.validate_connection_params()

    def test_connection_parameters_validation_sqlite(self):
        with self.assertRaises(ValueError):
            artifact = DatabaseQueryArtifact("jid@test.com", "password", "sqlite", {},
                                           query=self.query)
            artifact.validate_connection_params()

    @patch('sqlite3.connect', return_value=MagicMock())
    async def test_query_execution_sqlite(self, mocked_connect):
        artifact = DatabaseQueryArtifact("jid@test.com", "password", "sqlite",
                                       {'database': 'test.db'}, query=self.query)
        artifact.conn = mocked_connect()
        artifact.publish = AsyncMock()
        artifact.presence = MagicMock()
        artifact.presence.set_available = AsyncMock()
        artifact.cur = artifact.conn.cursor.return_value

        artifact.cur.fetchall.return_value = [("data1",), ("data2",)]
        data_processor = AsyncMock(return_value=[{"processed": "data"}])
        artifact.data_processor = data_processor

        await artifact.run()

        data_processor.assert_called_once()
        artifact.cur.execute.assert_called_with(self.query)
        artifact.cur.fetchall.assert_called_once()
        self.assertEqual(data_processor.call_args[0][0], [("data1",), ("data2",)])
