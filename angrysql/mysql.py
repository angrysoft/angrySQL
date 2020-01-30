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
import MySQLdb
import warnings
from .base import BaseDatabase

class MySqlConnection(BaseDatabase):
    def __init__(self, user, database, password='', charset='utf8', echo=False):
        """
        Create a connection to the database.
        :param config:
        :param echo:
        """
        super().__init__(echo=echo)
        try:
            self._conn = MySQLdb.connect(user=config.get('user'),
                                        password=config.get('password'),
                                        database=config.get('dbname'),
                                        charset='utf8')
            self._cur = self._conn.cursor()

        except MySQLdb.OperationalError as err:
            sys.stderr.write('Connection Error: {}\n'.format(err))
            sys.exit(1)
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

class MariaConnection(MySqlConnection):
    pass

class MysqlAdmin:
    def create_user(self, username, password=''):
        pass
    
    def delete_user(self, username):
        pass
    
    
# def create_db(adm, admpasswd, dbuser, dbpasswd, dbname):
#     info('Crete DB: {}'.format(dbname))
#     adm_conn = MySQLdb.connect(user=adm, password=admpasswd)
#     adm_cur = adm_conn.cursor()
#     adm_cur.execute("DROP USER IF EXISTS %s@localhost", (dbuser,))
#     adm_cur.execute("CREATE USER %s@localhost IDENTIFIED BY %s", (dbuser, dbpasswd))
#     adm_cur.execute("DROP DATABASE IF EXISTS {}".format(dbname))
#     adm_cur.execute('''CREATE DATABASE {}
#                        CHARACTER SET = "utf8"
#                        COLLATE = "utf8_general_ci"'''.format(dbname))
#     adm_cur.execute("GRANT ALL PRIVILEGES ON {}.* TO '{}'@'localhost'".format(dbname, dbuser))
#     adm_cur.execute("FLUSH PRIVILEGES")
#     adm_conn.commit()
#     adm_conn.close()