# Copyright 2019 AngrySoft Sebastian Zwierzchowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import sqlite3
from .base import BaseDatabase


class SqliteConnection(BaseDatabase):
    def __init__(self, dbfile=':memory:', echo=False):
        super().__init__(echo=echo)
        
        self.echo = echo
        try:
            self._conn = sqlite3.connect(dbfile)
            self._cur = self._conn.cursor()
            self._cur.execute('PRAGMA foreign_keys = ON')

        except sqlite3.OperationalError as err:
            sys.stderr.write('Connection Error: {}\n'.format(err))
            sys.exit(1)
        # warnings.filterwarnings("ignore", category=sqlite3.Warning)
    
    @property
    def primary_key(self):
        return 'PRIMARY KEY'
    
    @staticmethod
    def default(args):
        return f'DEFAULT {args}'

    @staticmethod
    def foreignkey(column_name, table_name, owner_column, column_full_name):
        return f"FOREIGN KEY({column_name}) REFERENCES {table_name}({owner_column})"
    
    def execute(self, sql, args=()):
        errors = None
        try:
            if self.echo:
                print(sql, args)
            self._cur.execute(sql, args)

        except sqlite3.IntegrityError as err:
            print(err)
            errors = err
        except sqlite3.OperationalError as err:
            print(err)
            errors = err
        except sqlite3.ProgrammingError as err:
            print(err)
            errors = err
        except Exception as err:
            print(f'something goes wrong: {err}')
        finally:
            return errors

    