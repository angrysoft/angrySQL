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
from .schema import Column, Integer, String

class BaseDatabase:
    __tabletemplate__ = 'CREATE TABLE IF NOT EXISTS {} ({})'
    _conn = None
    _cur = None

    def __init__(self, echo=False):
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
            # sqlite need foreign keys on end
            columns = list()
            for col in model.columns():
                columns.append(self.column_to_sql(col))

            for fkey in model.columns():
                if fkey.foreignkey:
                    columns.append(self.foreignkey_column_sql(fkey))

            self.execute(self.table_schema(model.table_name, columns))
        self.commit()

    def column_to_sql(self, column):
        opts = list()
        opts.append(column.column_name)
        opts.append(self.column_type(column.column_type))
        if column.primary_key:
            if isinstance(column.column_type, Integer):
                opts.append(self.primary_key)
            else:
                raise ValueError('Integer is needed')
        else:
            if column.unique:
                opts.append(self.unique)
            if not column.nullable:
                opts.append(self.notnull)
            if column.default is not None:
                opts.append(self.default(column.default))

        return ' '.join(opts)
    
    
    def foreignkey_column_sql(self, column):
        if column.foreignkey.find('.') < 0:
            raise ValueError('Proper value is tablename.columnname')
        tab, col = column.foreignkey.split('.', 1)

        return self.foreignkey(column_name=column.column_name,
                               table_name=tab,
                               owner_column=col,
                               column_full_name=column.column_full_name)

    def execute(self, sql, args=()):
        print(f'{sql} args = {args}')
        return ''

    # def fetch(self, one=None):
    #     rows = list()
    #     if one:
    #         r = self._cur.fetchone()
    #         if r:
    #             rows.append(r)
    #     else:
    #         rows = self._cur.fetchall()
    #     ret = []
    #     for row in rows:
    #         fields = {}
    #         for idx, col in enumerate(self._cur.description):
    #             fields[col[0]] = row[idx]
    #         ret.append(fields)
    #     return ret

    def fetch(self, model):
        ret = list()
        for row in self._cur.fetchall():
            ret.append(self._model(row, model))
        return ret
    
    def fetchone(self, model):
        row = self._cur.fetchone()
        if row:
            return self._model(row, model)
    
    def fetchmany(self, model, size=1):
        row = self._cur.fetchmany(size=self._cur.arraysize=size)
        if row:
            return self._model(row, model)
    
    def _model(self, row, model):
        new_model = model()
        for idx, col in enumerate(self._cur.description):
            if hasattr(new_model, col[0]):
                setattr(new_model, col[0], row[idx])
                
        for col in new_model.columns():
            _col = getattr(new_model, col.column_name)
            if isinstance(_col, Column):
                setattr(new_model, col.column_name, None)
            
        return new_model
                    
    def commit(self):
        self._conn.commit()
    
    def rollback(self):
        self._conn.rollback()
    
    def close(self):
        self._conn.close()

    @property
    def rowcount(self):
        return self._cur.rowcount

    def __del__(self):
        self.close()
        
    @staticmethod
    def table_schema(table_name, column_list):
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({','.join(column_list)})"
    
    @staticmethod
    def column_type(column_type):
        return str(column_type)

    @staticmethod
    def default(args):
        return f"DEFAULT '{args}'"
    
    @property
    def unique(self):
        return 'UNIQUE'
    
    @property
    def primary_key(self):
        return 'NOT NULL AUTO_INCREMENT PRIMARY KEY'
    
    @property
    def notnull(self):
        return 'NOT NULL'
    
    @staticmethod
    def foreignkey(column_name, table_name, owner_column, column_full_name):
        return f"CONSTRAINT fk_{column_full_name.replace('.', '_')} FOREIGN KEY({column_name}) REFERENCES {table_name}({owner_column})"

        
class BaseQuery:
    __db__ = None

    def __init__(self, model):
        if not isinstance(model, MetaBaseModel) and not isinstance(model, BaseModel):
            raise ValueError('This is not a model object')
        self.model = model
        self.model_columns = model.columns()
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
        self._sql_base = f"SELECT {','.join([c.column_full_name for c in self.model_columns])} FROM {model.table_name}"

    def get(self, model_id):
            self.__db__.execute(f"{self._sql_base} WHERE {self._get_primary_key_name()} = '{model_id}'")
            return self.__db__.fetchone(self.model)
    
    def _get_primary_key_name(self):
        for c in self.model_columns:
            if c.primary_key:
                return c.column_name
    
    def columns(self, *cols):
        self._sql_base = f"SELECT {','.join([c.column_full_name for c in cols])} FROM {self.model.table_name}"
        return self

    def all(self):
        self.__db__.execute(self.sql)
        return self.__db__.fetch(self.model)

    def one(self):
        self.__db__.execute(self.sql)
        return  self.__db__.fetchone(self.model)
    
    def many(self, size):
        self.__db__.execute(self.sql)
        return self.__db__.fetchmany(self.model, size)

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

        self._sql_base = f'INSERT INTO {model.table_name} {self._get_column_and_values()}'
        # self.errors = self.__db__.execute(self.sql)

    def _get_column_and_values(self):
        #TODO add check if columnt is nullable
        values = list()
        names = list()
        for c in self.model_columns:
            val = getattr(self.model, c.column_name)
            if not isinstance(val, Column):
                names.append(c.column_name)
                values.append(f"'{val}'")
        return f"({','.join(names)}) VALUES ({','.join(values)})"
    
    def do(self):
        self.errors = self.__db__.execute(self.sql)
        return self.__db__.rowcount


class Update(BaseQuery):
    def __init__(self, model):
        super(Update, self).__init__(model)
        self._sql_base = f"UPDATE {model.table_name} SET {self._get_column_and_values()}"

    def do(self):
        self.errors = self.__db__.execute(self.sql)
        return self.__db__.rowcount

    def where(self, *conditions):
        self._where.extend(conditions)
        return self

    def _get_column_and_values(self):
        values = list()
        for c in self.model_columns:
            val = getattr(self.model, c.column_name)
            if not isinstance(val, Column):
                values.append("{} = '{}'".format(c.column_full_name,val))
        return ','.join(values)


class Delete(BaseQuery):
    def __init__(self, model):
        super(Delete, self).__init__(model)
        self._sql_base = f'DELETE FROM {model.table_name}'

    def where(self, *conditions):
        self._where.extend(conditions)
        return self

    def do(self):
        self.__db__.execute(self.sql)
        return self.__db__.rowcount


class Join(Select):
    def __init__(self, *models):
        self.model_columns = list()
        self._joins = list()
        self._where = list()
        self._order = list()
        for item in models:
            if isinstance(item, Column):
                self.model_columns.append(item)
            elif isinstance(item, BaseModel) or isinstance(item, MetaBaseModel):
                for col in item.columns():
                    self.model_columns.append(col)

        self._sql_base = 'SELECT {} FROM {}'.format(
                ','.join(['{} AS {}'.format(c.column_full_name,
                                            self._get_column_alias(c.column_full_name)) for c in self.model_columns]),
                self._get_table_name())

    @staticmethod
    def _get_column_alias(column_name):
        if column_name.find('.') < 0:
            raise ValueError('name is invalid')
        table, column = column_name.split('.', 1)
        return '_'.join([table, column])

    def _get_table_name(self):
        full_name = self.model_columns[0].column_full_name
        return full_name.split('.', 1)[0]

    def inner(self, table_name, condition):
        if isinstance(table_name, BaseModel) or isinstance(table_name, MetaBaseModel):
            table_name = table_name.table_name
        self._joins.append('INNER JOIN {} ON {}'.format(table_name, condition))
        return self

    def all(self):
        self.__db__.execute(self.sql)
        func = {}
        for c in self.model_columns:
            print(self._get_column_alias(c.column_full_name))
            func[self._get_column_alias(c.column_full_name)] = Column(String())

        Model = type('Model', (BaseModel,), func)

        return self.__db__.fetch(Model)

    @property
    def sql(self):
        ret_sql = self._sql_base
        if self._joins:
            ret_sql += ' '
            ret_sql += ' '.join(self._joins)
        if self._where:
            ret_sql += f" WHERE {' AND '.join(self._where)}"
        if self._order:
            ret_sql += f" ORDER BY {','.join(self._order)}"
        return ret_sql


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
    
    def __init__(self, **args):
        for k in args:
            if hasattr(self, k):
                setattr(self, k, args[k])
            else:
                raise ValueError(f'{k}: column name not in model')
    
    def __str__(self):
        ret = ''
        for x in self.columns():
            ret += f'{x.column_name} : {getattr(self, x.column_name)} '
        return ret
            

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