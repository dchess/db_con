from os import getenv
from sqlalchemy import bindparam, create_engine, delete, inspect, Table, MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.sql import text as sa_text
from sqlalchemy.schema import DropTable
import pandas as pd

try:
    from pyodbc import drivers
except ImportError:
    drivers = None


ENV_CONFIG = {
    "dialect": getenv("DB_DIALECT"),
    "user": getenv("DB_USER"),
    "pwd": getenv("DB_PWD"),
    "server": getenv("DB_SERVER"),
    "port": getenv("DB_PORT"),
    "db": getenv("DB"),
    "schema": getenv("DB_SCHEMA"),
}


class Connection:
    def __init__(
        self,
        dialect=None,
        user=None,
        pwd=None,
        server=None,
        port=None,
        db=None,
        schema=None,
    ):
        self.dialect = dialect
        self.schema = schema
        self.db = db
        self.options = {
            "username": user,
            "password": pwd,
            "host": server,
            "port": port,
            "database": db,
        }
        self.helpers = {}
        self.engine = self._get_engine()

    def _cstr(self):
        """
        Constructs SQLAlchemy connection string.
        """
        return URL(self.dialect, **self.options)

    def _add_mssql_options(self):
        """
        Adds MS SQL specific connection options for creating engine.
        """
        if self.dialect == "mssql":
            try:
                self.options["query"] = {"driver": sorted(drivers()).pop()}
                self.helpers["fast_executemany"] = True
            except ValueError as e:
                print(e)

    def _add_postgres_options(self):
        """
        Adds PostgreSQL specific connection options for creating engine.
        """
        if "postgres" in self.dialect:
            self.helpers["executemany_mode"] = "batch"

    def _add_oracle_options(self):
        """
        Adds Oracle specific connection options for creating engine.
        """
        if "oracle" in self.dialect:
            if self.schema == "SYS" or self.options["username"] == "SYS":
                self.options["query"] = {"mode": "SYSDBA"}
            self.helpers["max_identifier_length"] = 128

    def _get_engine(self):
        """
        Sets database engine for connections.
        """
        self._add_mssql_options()
        self._add_postgres_options()
        self._add_oracle_options()
        return create_engine(self._cstr(), **self.helpers)

    def query(self, sql_query, params=None):
        """
        Returns results of SQL query as pandas dataframe.
        """
        return pd.read_sql_query(sql_query, con=self.engine, params=params)

    def insert_into(self, table, df, if_exists="append", chunksize=None, dtype=None):
        """
        Inserts pandas dataframe into database table.
        """
        df.to_sql(
            table,
            con=self.engine,
            schema=self.schema,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
            dtype=dtype,
        )

    def table(self, tablename):
        """
        Returns SQLAlchemy Table object.
        """
        return Table(
            tablename,
            MetaData(),
            autoload=True,
            autoload_with=self.engine,
            schema=self.schema,
        )

    def drop(self, tablename):
        """
        Drops database table if it exists.
        """
        if self.engine.has_table(tablename):
            table = self.table(tablename)
            self.engine.execute(DropTable(table))

    def select_all(self, tablename):
        """
        Returns all data from a specified database table.
        """
        return pd.read_sql_table(tablename, con=self.engine, schema=self.schema)

    def exec_cmd(self, command, params=None, autocommit=True):
        """
        Executes raw SQL command w/ optional params.
        """
        bindparams = []
        if params:
            for key, value in params.items():
                bindparams.append(bindparam(key, value=value))
        cmd = sa_text(command).execution_options(autocommit=autocommit)
        return self.engine.execute(cmd.bindparams(*bindparams))

    def get_columns(self, table):
        """
        Returns list of column names for a table.
        """
        inspector = inspect(self.engine)
        return inspector.get_columns(table, schema=self.schema)

    def get_view_definition(self, view):
        """
        Returns the text definition of a specified view.
        """
        inspector = inspect(self.engine)
        return inspector.get_view_definition(view, schema=self.schema)

    def delete(self, tablename):
        """
        Deletes all rows in a table.
        """
        metadata = MetaData()
        table = Table(
            tablename,
            metadata,
            autoload=True,
            autoload_with=self.engine,
            schema=self.schema,
        )
        self.engine.execute(delete(table))

    def _read_sql_file(self, filename):
        """
        Reads a sql file into a sql query string
        """
        if filename.lower().endswith(".sql"):
            with open(filename) as f:
                return f.read()
        else:
            raise Exception(f"{filename} is not a valid .sql file")

    def query_from_file(self, filename):
        pass

    def exec_cmd_from_file(self, filename):
        pass
