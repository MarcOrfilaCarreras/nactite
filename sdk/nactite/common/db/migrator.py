import importlib
import os
import pkgutil
import sqlite3
from typing import Set


class DatabaseMigrator:
    """
    A class to handle database migrations using SQLite.

    Attributes:
        db_path (str): Path to the SQLite database file.
        migrations_path (str): Directory path where migration files are stored.
    """

    def __init__(self, db_path: str = 'cache.db', migrations_package: str = 'nactite.common.db.migrations') -> None:
        """
        Initializes the DatabaseMigrator with paths for the database and migrations.

        Args:
            db_path (str): Path to the SQLite database file. Defaults to 'cache.db'.
            migrations_package (str): Package path where migration files are stored. Defaults to 'nactite.intranet.db.migrations'.
        """
        self.db_path = db_path
        self.migrations_package = migrations_package

    def _connect(self) -> sqlite3.Connection:
        """
        Establishes and returns a connection to the SQLite database.

        Returns:
            sqlite3.Connection: The SQLite connection object.
        """
        return sqlite3.connect(self.db_path)

    def create_migration_table(self, conn: sqlite3.Connection) -> None:
        """
        Creates the migrations table if it does not already exist.

        Args:
            conn (sqlite3.Connection): The SQLite connection object.
        """
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration TEXT UNIQUE,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        conn.commit()

    def get_applied_migrations(self, conn: sqlite3.Connection) -> Set[str]:
        """
        Retrieves a set of applied migration filenames from the database.

        Args:
            conn (sqlite3.Connection): The SQLite connection object.

        Returns:
            Set[str]: A set of filenames of applied migrations.
        """
        cursor = conn.cursor()
        cursor.execute('SELECT migration FROM migrations')
        rows = cursor.fetchall()
        return {row[0] for row in rows}

    def apply_migration(self, conn: sqlite3.Connection, module_name: str) -> None:
        """
        Applies a migration by executing the SQL script in the specified file.

        Args:
            conn (sqlite3.Connection): The SQLite connection object.
            module_name (str): Name of the module to migrate.
        """
        module = importlib.import_module(f'{module_name}')
        sql = module.get_sql()

        cursor = conn.cursor()
        cursor.executescript(sql)
        cursor.execute('INSERT INTO migrations (migration) VALUES (?)',
                       (module_name,))
        conn.commit()

    def migrate(self) -> None:
        """
        Runs all unapplied migrations in the migrations directory.
        """
        conn = self._connect()
        try:
            self.create_migration_table(conn)
            applied_migrations = self.get_applied_migrations(conn)

            package = importlib.import_module(self.migrations_package)
            migration_modules = [name for _, name, _ in pkgutil.iter_modules(
                package.__path__, f'{self.migrations_package}.')]

            for module_name in migration_modules:
                if module_name not in applied_migrations:
                    print(f'Applying migration: {module_name}')
                    self.apply_migration(conn, module_name)
                else:
                    print(f'Skipping already applied migration: {module_name}')

        finally:
            conn.close()
