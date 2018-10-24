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
import sys
import datetime
import sqlite3

# __all__ = [
#     'Column',
#     'Integer',
#     'SmallInteger',
#     'BigInt',
#     'String',
#     'Base',
#
# ]


def or_(*args):
    return ' OR '.join(args)


def and_(*args):
    return ' AND '.join(args)


class ColumnType:
    __columntype__ = ''

    def __str__(self):
        return self.__columntype__


class Integer(ColumnType):
    __columntype__ = 'int'
    __unsigned__ = False
    __zerofill__ = False

    def __init__(self, unsigned=False, zerofill=False):
        self.__unsigned__ = unsigned
        self.__zerofill__ = zerofill

    def __str__(self):
        if self.__unsigned__:
            return '{} unsigned'.format(self.__columntype__)
        elif self.__zerofill__:
            return '{} zerofill'.format(self.__columntype__)
        else:
            return self.__columntype__


class TinyInteger(Integer):
    __columntype__ = 'int'


class SmallInteger(Integer):
    __columntype__ = 'smallint'


class BigInt(Integer):
    __columntype__ = 'bigint'


class String(ColumnType):
    __columntype__ = 'text'

    def __init__(self, size=None):
        if size:
            if not type(size) == int and size > 255:
                raise ValueError('value of size is incorrect')
            self.__columntype__ = 'varchar({})'.format(size)


class Year(ColumnType):
    __columntype__ = 'year'

    def __init__(self, size=None):
        if size:
            self.__columntype__ += '({})'.format(size)


class Date(ColumnType):
    __columntype__ = 'date'


class Time(ColumnType):
    __columntype__ = 'time'


class DataTime(Year):
    __columntype__ = 'datatime'


class TimeStamp(ColumnType):
    __columntype__ = 'timestamp'


class Column:

    def __init__(self, column_type, nullable=True, unique=False, default=None,
                 primary_key=False, foreignkey=None, cascade=None, unsigned=False, ):
        self.column_type = column_type
        self.nullable = nullable
        self.unique = unique
        self.column_name = ''
        self.column_full_name = ''
        self.default = default
        self.primary_key = primary_key
        self.foreignkey = foreignkey
        self.cascade = cascade
        self.unsigned = unsigned
        self._value = ''

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = _value

    def like(self, other):
        return "{} LIKE '{}'".format(self.column_full_name, other)

    def _in(self, args):
        if type(args) == list:
            value_list = ', '.join(["'{}'".format(a) for a in args])
        else:
            raise ValueError('list required not {}'.format(type(args)))
        return "IN ({})".format(value_list)

    def in_(self, args):
        return '{} {}'.format(self.self.column_full_name, self._in(args))

    def not_in(self, args):
        return '{} NOT {}'.format(self.column_full_name, self._in(args))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return '{} = {}'.format(self.column_full_name, other.column_full_name)
        return "{} = '{}'".format(self.column_full_name, other)

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return '{} != {}'.format(self.column_full_name, other.column_full_name)
        return "{} != '{}'".format(self.column_full_name, other)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return '{} < {}'.format(self.column_full_name, other.column_full_name)
        return "{} < '{}'".format(self.column_full_name, other)

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return '{} <= {}'.format(self.column_full_name, other.column_full_name)
        return "{} <= '{}'".format(self.column_full_name, other)

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return '{} > {}'.format(self.column_full_name, other.column_full_name)
        return "{} > '{}'".format(self.column_full_name, other)

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return '{} >= {}'.format(self.column_full_name, other.column_full_name)
        return "{} >= '{}'".format(self.column_full_name, other)

    @property
    def sql(self):
        opts = list()
        opts.append(self.column_name)
        opts.append(str(self.column_type))
        if self.primary_key:
            if isinstance(self.column_type, Integer):
                opts.append('NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.column_type))
            else:
                raise ValueError('Integer is needed')
        else:
            if self.unique:
                opts.append('UNIQUE')
            if not self.nullable:
                opts.append('NOT NULL')
            if self.default:
                opts.append("DEFAULT '{}'".format(self.default))

        if self.foreignkey:
            if self.foreignkey.find('.') < 0:
                raise ValueError('Proper value is tablename.columnname')
            tab, col = self.foreignkey.split('.', 1)
            opts.append(',')
            opts.append('CONSTRAINT fk_{fullname} FOREIGN KEY({name}) REFERENCES {table}({owner})'.format(
                name=self.column_name, table=tab, owner=col, fullname=self.column_full_name.replace('.', '_')))
        return ' '.join(opts)

    def __str__(self):
        return self.column_full_name


class BaseQuery:
    __db__ = None

    def __init__(self, model):
        if not isinstance(model, MetaBaseModel) and not isinstance(model, BaseModel):
            raise ValueError('This is not a model object')
        self.model = model
        self.columns = model.columns()
        self._where = list()
        self._order = list()
        self._sql_base = ''
        self.errors = None

    @property
    def sql(self):
        ret_sql = self._sql_base
        if self._where:
            ret_sql += ' WHERE {}'.format(' AND '.join(self._where))
        if self._order:
            ret_sql += ' ORDER BY {}'.format(','.join(self._order))
        return ret_sql


class Select(BaseQuery):
    def __init__(self, model):
        super(Select, self).__init__(model)
        self._sql_base = 'SELECT {} FROM {}'.format(
            ','.join([c.column_full_name for c in self.columns]),
            model.table_name)

    def get(self, model_id):
        for c in self.columns:
            if c.primary_key:
                self.__db__.execute("{} WHERE {} = '{}'".format(self._sql_base, c.column_name, model_id))
                if self.__db__.rowcount > 0:
                    return self.__db__.fetch_model(self.model, one=True)[0]
                return None

    def all(self):
        self.__db__.execute(self.sql)
        if self.__db__.rowcount > 0:
            return self.__db__.fetch_model(self.model)
        return []

    def first(self):
        self.__db__.execute(self.sql)
        if self.__db__.rowcount > 0:
            return self.__db__.fetch_model(self.model, one=True)[0]
        return None

    def where(self, *conditions):
        self._where.extend(conditions)
        return self

    def order_by(self, *columns, desc=False):
        for order_column in columns:
            col = ''
            if isinstance(order_column, Column):
                col = order_column.column_full_name
            elif type(order_column) == str:
                col = order_column
            if desc:
                col += ' DESC'
            else:
                col += ' ASC'
            self._order.append(col)

        return self


class Insert(BaseQuery):
    def __init__(self, model):
        super(Insert, self).__init__(model)

        self._sql_base = 'INSERT INTO {} {}'.format(model.table_name,
                                                    self._get_column_and_values())

        self.errors = self.__db__.execute(self.sql)

    def _get_column_and_values(self):
        values = list()
        names = list()
        for c in self.columns:
            val = getattr(self.model, c.column_name)
            if not isinstance(val, Column):
                names.append(c.column_full_name)
                values.append("'{}'".format(val))
        return '({}) VALUES ({})'.format(','.join(names), ','.join(values))


class Update(BaseQuery):
    def __init__(self, model):
        super(Update, self).__init__(model)
        self._sql_base = 'UPDATE {} SET {}'.format(model.table_name,
                                                   self._get_column_and_values())

    def all(self):
        self.errors = self.__db__.execute(self.sql)
        return self.__db__.rowcount

    def where(self, *conditions):
        self._where.extend(conditions)
        return self

    def _get_column_and_values(self):
        values = list()
        for c in self.columns:
            val = getattr(self.model, c.column_name)
            if not isinstance(val, Column):
                values.append("{} = '{}'".format(c.column_full_name,val))
        return ','.join(values)


class Delete(BaseQuery):
    def __init__(self, model):
        super(Delete, self).__init__(model)
        self._sql_base = 'DELETE FROM {}'.format(model.table_name)

    def where(self, *conditions):
        self._where.extend(conditions)
        return self

    def all(self):
        self.__db__.execute(self.sql)
        return self.__db__.rowcount


class Join(Select):
    def __init__(self, *models):
        self.columns = list()
        self._joins = list()
        self._where = list()
        self._order = list()
        for item in models:
            if isinstance(item, Column):
                self.columns.append(item)
            elif isinstance(item, BaseModel) or isinstance(item, MetaBaseModel):
                for col in item.columns():
                    self.columns.append(col)

        self._sql_base = 'SELECT {} FROM {}'.format(
                ','.join(['{} AS {}'.format(c.column_full_name,
                                            self._get_column_alias(c.column_full_name)) for c in self.columns]),
                self._get_table_name())

    @staticmethod
    def _get_column_alias(column_name):
        if column_name.find('.') < 0:
            raise ValueError('name is invalid')
        table, column = column_name.split('.', 1)
        return '_'.join([table, column])

    def _get_table_name(self):
        full_name = self.columns[0].column_full_name
        return full_name.split('.', 1)[0]

    def inner(self, table_name, condition):
        if isinstance(table_name, BaseModel) or isinstance(table_name, MetaBaseModel):
            table_name = table_name.table_name
        self._joins.append('INNER JOIN {} ON {}'.format(table_name, condition))
        return self

    def all(self):
        self.__db__.execute(self.sql)
        if self.__db__.rowcount > 0:
            func = {}
            for c in self.columns:
                print(self._get_column_alias(c.column_full_name))
                func[self._get_column_alias(c.column_full_name)] = Column(String())

            Model = type('Model', (BaseModel,), func)

            return self.__db__.fetch_model(Model)
        return []

    @property
    def sql(self):
        ret_sql = self._sql_base
        if self._joins:
            ret_sql += ' '
            ret_sql += ' '.join(self._joins)
        if self._where:
            ret_sql += ' WHERE {}'.format(' AND '.join(self._where))
        if self._order:
            ret_sql += ' ORDER BY {}'.format(','.join(self._order))
        return ret_sql


class BaseDatabase:
    __tabletemplate__ = 'CREATE TABLE IF NOT EXISTS {} ({})'
    conn = None
    cur = None

    def __init__(self, config, echo=False):
        Select.__db__ = self
        Insert.__db__ = self
        Update.__db__ = self
        Delete.__db__ = self
        Join.__db__ = self
        self.select = Select
        self.insert = Insert
        self.update = Update
        self.delete = Delete
        self.join = Join

        self.echo = echo

    def create_tables(self, *models):
        for model in models:
            sql = self.__tabletemplate__.format(model.table_name,
                                                ','.join([c.sql for c in model.columns()]))
            self.execute(sql)
        self.commit()

    def execute(self, sql, args=()):
        if self.echo:
            print(sql, args)
        self.cur.execute(sql, args)

    def fetch(self, one=None):
        if one:
            rows = (self.cur.fetchone(),)
        else:
            rows = self.cur.fetchall()
        ret = []
        for row in rows:
            fields = {}
            for idx, col in enumerate(self.cur.description):
                fields[col[0]] = row[idx]
            ret.append(fields)
        return ret

    def fetch_model(self, model, one=False):
        if one:
            rows = (self.cur.fetchone(),)
        else:
            rows = self.cur.fetchall()

        ret = []

        for row in rows:
            new_model = model()
            for idx, col in enumerate(self.cur.description):
                if hasattr(new_model, col[0]):
                    setattr(new_model, col[0], row[idx])
            ret.append(new_model)
        return ret

    def commit(self):
        self.conn.commit()

    @property
    def rowcount(self):
        return self.cur.rowcount

    def __del__(self):
        self.conn.close()


class MySqlDatabase(BaseDatabase):
    __tabletemplate__ = 'CREATE TABLE IF NOT EXISTS {} ({}) ENGINE=InnoDB'

    def __init__(self, config, echo=False):
        super(MySqlDatabase, self).__init__(config, echo=echo)
        try:
            self.conn = MySQLdb.connect(user=config.get('user'),
                                        password=config.get('password'),
                                        database=config.get('dbname'),
                                        charset='utf8')
            self.cur = self.conn.cursor()

        except MySQLdb.OperationalError as err:
            sys.stderr.write('Connection Error: {}\n'.format(err))
            sys.exit(1)
        warnings.filterwarnings("ignore", category=MySQLdb.Warning)

    def execute(self, sql, args=()):
        errors = None
        try:
            if self.echo:
                print(sql, args)
            self.cur.execute(sql, args)

        except MySQLdb.IntegrityError as err:
            print(err)
            errors = err
        except MySQLdb.OperationalError as err:
            print(err)
            errors = err
        except MySQLdb.ProgrammingError as err:
            print(err)
            errors = err
        except:
            print('something goes wrong')
        finally:
            return errors


class SqliteDatabase(BaseDatabase):
    __tabletemplate__ = 'CREATE TABLE IF NOT EXISTS {} ({})'

    def __init__(self, config, echo=False):
        super(SqliteDatabase, self).__init__(config, echo=echo)
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


class MetaBaseModel(type):

    def __new__(mcs, name, bases, attrs):
        result = type.__new__(mcs, name, bases, attrs)
        result.columns_obj = list()

        table_name = ''
        for i, c in enumerate(name):
            if i > 0 and c.isupper():
                table_name += '_'
            table_name += c
        result.table_name = table_name.lower()

        for obj_name in attrs:
            obj = getattr(result, obj_name)
            if not obj_name.startswith('_') and isinstance(obj, Column):
                obj.column_name = obj_name
                obj.column_full_name = '{}.{}'.format(result.table_name, obj_name)
                result.columns_obj.append(obj)

        table_name = ''
        for i, c in enumerate(name):
            if i > 0 and c.isupper():
                table_name += '_'
            table_name += c
        result.table_name = table_name.lower()
        return result


class BaseModel(metaclass=MetaBaseModel):
    @classmethod
    def columns(cls):
        return cls.columns_obj

    # def __setattr__(self, key, value):
    #     attr = self.__getattribute__(key)
    #     if isinstance(attr, Column):
    #         attr.value = value
    #     else:
    #         object.__setattr__(self, key, value)

    # def __getattribute__(self, item):
    #     attr = object.__getattribute__(self, item)
    #     if isinstance(attr, Column):
    #         return attr.value
    #     else:
    #         return attr








