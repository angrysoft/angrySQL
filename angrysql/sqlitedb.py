# Copyright 2018 AngrySoft Sebastian Zwierzchowski
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
import warnings
from .schema import BaseDatabase


class Connection(BaseDatabase):
    """Sqlite3 Database Connection"""
    __tabletemplate__ = 'CREATE TABLE IF NOT EXISTS {} ({})'

    def __init__(self, config, echo=False):
        super(Connection, self).__init__(config, echo=echo)
        try:
            self.conn = sqlite3.connect(config.get('dbfile', ':memory:'))
            self.cur = self.conn.cursor()

        except sqlite3.OperationalError as err:
            sys.stderr.write('Connection Error: {}\n'.format(err))
            sys.exit(1)
        warnings.filterwarnings("ignore", category=sqlite3.Warning)

    def execute(self, sql, args=()):
        errors = None
        try:
            if self.echo:
                print(sql, args)
            self.cur.execute(sql, args)

        except sqlite3.IntegrityError as err:
            print(err)
            errors = err
        except sqlite3.OperationalError as err:
            print(err)
            errors = err
        except sqlite3.ProgrammingError as err:
            print(err)
            errors = err
        except:
            print('something goes wrong')
        finally:
            return errors
