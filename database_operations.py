import os
from typing import Dict, Any, List, Optional, Union
import sqlite3
import mysql.connector
import psycopg
import pymongo
from sqlalchemy import create_engine, text
import pandas as pd
import json
from datetime import datetime
import csv
import yaml

class DatabaseOperations:
    def __init__(self):
        self.connections = {}
        self.engines = {}

    def connect_database(self, db_type: str, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Connect to a database.
        Args:
            db_type: Type of database ('sqlite', 'mysql', 'postgresql', 'mongodb')
            connection_params: Connection parameters
        """
        try:
            if db_type == 'sqlite':
                conn = sqlite3.connect(connection_params.get('database', ':memory:'))
                self.connections[db_type] = conn
            elif db_type == 'mysql':
                conn = mysql.connector.connect(
                    host=connection_params.get('host', 'localhost'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password'),
                    database=connection_params.get('database')
                )
                self.connections[db_type] = conn
            elif db_type == 'postgresql':
                conn = psycopg.connect(
                    host=connection_params.get('host', 'localhost'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password'),
                    dbname=connection_params.get('database')
                )
                self.connections[db_type] = conn
            elif db_type == 'mongodb':
                client = pymongo.MongoClient(connection_params.get('uri'))
                db = client[connection_params.get('database')]
                self.connections[db_type] = db
            else:
                return {"error": f"Unsupported database type: {db_type}"}

            return {"success": True, "message": f"Connected to {db_type} database"}
        except Exception as e:
            return {"error": str(e)}

    def create_database(self, db_type: str, name: str, connection_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new database.
        Args:
            db_type: Type of database to create
            name: Name of the database
            connection_params: Connection parameters
        """
        try:
            if db_type == 'sqlite':
                conn = sqlite3.connect(name)
                self.connections[db_type] = conn
            elif db_type == 'mysql':
                conn = mysql.connector.connect(
                    host=connection_params.get('host', 'localhost'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password')
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE {name}")
                conn.close()
            elif db_type == 'postgresql':
                conn = psycopg.connect(
                    host=connection_params.get('host', 'localhost'),
                    user=connection_params.get('user'),
                    password=connection_params.get('password')
                )
                conn.autocommit = True
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE {name}")
                conn.close()
            elif db_type == 'mongodb':
                client = pymongo.MongoClient(connection_params.get('uri'))
                client[name]
            else:
                return {"error": f"Unsupported database type: {db_type}"}

            return {"success": True, "message": f"Created {db_type} database: {name}"}
        except Exception as e:
            return {"error": str(e)}

    def execute_query(self, db_type: str, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a database query.
        Args:
            db_type: Type of database
            query: Query to execute
            params: Query parameters
        """
        try:
            if db_type not in self.connections:
                return {"error": f"No connection to {db_type} database"}

            if db_type == 'mongodb':
                # MongoDB queries are handled differently
                collection = self.connections[db_type][query.get('collection')]
                result = collection.find(query.get('filter', {}))
                return {"success": True, "results": list(result)}
            else:
                cursor = self.connections[db_type].cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    return {
                        "success": True,
                        "results": [dict(zip(columns, row)) for row in results]
                    }
                else:
                    self.connections[db_type].commit()
                    return {
                        "success": True,
                        "message": f"Query executed successfully. Rows affected: {cursor.rowcount}"
                    }
        except Exception as e:
            return {"error": str(e)}

    def backup_database(self, db_type: str, backup_path: str) -> Dict[str, Any]:
        """
        Create a backup of the database.
        Args:
            db_type: Type of database
            backup_path: Path to save the backup
        """
        try:
            if db_type == 'sqlite':
                with open(backup_path, 'w') as f:
                    for line in self.connections[db_type].iterdump():
                        f.write(f'{line}\n')
            elif db_type == 'mysql':
                os.system(f"mysqldump -u {self.connections[db_type].user} -p{self.connections[db_type].password} "
                         f"{self.connections[db_type].database} > {backup_path}")
            elif db_type == 'postgresql':
                os.system(f"pg_dump -U {self.connections[db_type].user} -d {self.connections[db_type].database} "
                         f"-f {backup_path}")
            elif db_type == 'mongodb':
                os.system(f"mongodump --uri {self.connections[db_type].client.address} "
                         f"--db {self.connections[db_type].name} --out {backup_path}")
            else:
                return {"error": f"Unsupported database type: {db_type}"}

            return {"success": True, "message": f"Database backup created at {backup_path}"}
        except Exception as e:
            return {"error": str(e)}

    def restore_database(self, db_type: str, backup_path: str) -> Dict[str, Any]:
        """
        Restore a database from backup.
        Args:
            db_type: Type of database
            backup_path: Path to the backup file
        """
        try:
            if db_type == 'sqlite':
                with open(backup_path, 'r') as f:
                    self.connections[db_type].executescript(f.read())
            elif db_type == 'mysql':
                os.system(f"mysql -u {self.connections[db_type].user} -p{self.connections[db_type].password} "
                         f"{self.connections[db_type].database} < {backup_path}")
            elif db_type == 'postgresql':
                os.system(f"psql -U {self.connections[db_type].user} -d {self.connections[db_type].database} "
                         f"-f {backup_path}")
            elif db_type == 'mongodb':
                os.system(f"mongorestore --uri {self.connections[db_type].client.address} "
                         f"--db {self.connections[db_type].name} {backup_path}")
            else:
                return {"error": f"Unsupported database type: {db_type}"}

            return {"success": True, "message": "Database restored successfully"}
        except Exception as e:
            return {"error": str(e)}

    def migrate_data(self, source_type: str, target_type: str, 
                    source_params: Dict[str, Any], target_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate data between different database types.
        Args:
            source_type: Source database type
            target_type: Target database type
            source_params: Source connection parameters
            target_params: Target connection parameters
        """
        try:
            # Connect to source and target databases
            self.connect_database(source_type, source_params)
            self.connect_database(target_type, target_params)

            if source_type == 'mongodb':
                # Handle MongoDB to SQL migration
                collections = self.connections[source_type].list_collection_names()
                for collection in collections:
                    data = list(self.connections[source_type][collection].find())
                    if target_type in ['mysql', 'postgresql']:
                        # Convert MongoDB documents to SQL tables
                        df = pd.DataFrame(data)
                        df.to_sql(collection, self.connections[target_type], if_exists='replace')
            else:
                # Handle SQL to SQL or SQL to MongoDB migration
                cursor = self.connections[source_type].cursor()
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    data = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]

                    if target_type == 'mongodb':
                        # Convert SQL data to MongoDB documents
                        documents = [dict(zip(columns, row)) for row in data]
                        self.connections[target_type][table_name].insert_many(documents)
                    else:
                        # Convert SQL data to another SQL database
                        df = pd.DataFrame(data, columns=columns)
                        df.to_sql(table_name, self.connections[target_type], if_exists='replace')

            return {"success": True, "message": "Data migration completed successfully"}
        except Exception as e:
            return {"error": str(e)}

    def export_data(self, db_type: str, query: str, format: str, output_path: str) -> Dict[str, Any]:
        """
        Export data from database to various formats.
        Args:
            db_type: Type of database
            query: Query to execute
            format: Export format ('csv', 'json', 'excel', 'yaml')
            output_path: Path to save the exported data
        """
        try:
            if db_type not in self.connections:
                return {"error": f"No connection to {db_type} database"}

            if db_type == 'mongodb':
                collection = self.connections[db_type][query.get('collection')]
                data = list(collection.find(query.get('filter', {})))
                df = pd.DataFrame(data)
            else:
                df = pd.read_sql_query(query, self.connections[db_type])

            if format == 'csv':
                df.to_csv(output_path, index=False)
            elif format == 'json':
                df.to_json(output_path, orient='records')
            elif format == 'excel':
                df.to_excel(output_path, index=False)
            elif format == 'yaml':
                with open(output_path, 'w') as f:
                    yaml.dump(df.to_dict('records'), f)
            else:
                return {"error": f"Unsupported export format: {format}"}

            return {"success": True, "message": f"Data exported successfully to {output_path}"}
        except Exception as e:
            return {"error": str(e)}

# Create a singleton instance
database_operations = DatabaseOperations() 