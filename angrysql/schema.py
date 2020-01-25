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


def or_(*args):
    return ' OR '.join(args)


def and_(*args):
    return ' AND '.join(args)


class ColumnType:
    __columntype__ = ''

    def __str__(self):
        return self.__columntype__


class Integer(ColumnType):
    __columntype__ = 'integer'
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
        return '{} {}'.format(self.column_full_name, self._in(args))

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

    # @property
    # def sql(self):
    #     opts = list()
    #     opts.append(self.column_name)
    #     opts.append(str(self.column_type))
    #     if self.primary_key:
    #         if isinstance(self.column_type, Integer):
    #             opts.append('NOT NULL AUTO_INCREMENT PRIMARY KEY'.format(self.column_type))
    #         else:
    #             raise ValueError('Integer is needed')
    #     else:
    #         if self.unique:
    #             opts.append('UNIQUE')
    #         if not self.nullable:
    #             opts.append('NOT NULL')
    #         if self.default:
    #             opts.append("DEFAULT '{}'".format(self.default))

    #     if self.foreignkey:
    #         if self.foreignkey.find('.') < 0:
    #             raise ValueError('Proper value is tablename.columnname')
    #         tab, col = self.foreignkey.split('.', 1)
    #         opts.append(',')
    #         opts.append('CONSTRAINT fk_{fullname} FOREIGN KEY({name}) REFERENCES {table}({owner})'.format(
    #             name=self.column_name, table=tab, owner=col, fullname=self.column_full_name.replace('.', '_')))
    #     return ' '.join(opts)

    def __str__(self):
        return self.column_full_name


