class Sql:
    create_table = 'CREATE TABLE IF NOT EXISTS {} ({})'
    primary_key = 'NOT NULL AUTO_INCREMENT PRIMARY KEY'
    unique = 'UNIQUE'
    notnull = 'NOT NULL'

    @property
    def name(self):
        return self.__class__.__name__

    @staticmethod
    def column_type(column_type):
        return str(column_type)

    @staticmethod
    def default(args):
        return "DEFAULT '{}'".format(args)

    @staticmethod
    def foreignkey(column_name, table_name, owner_column, column_full_name):
        return 'CONSTRAINT fk_{fullname} FOREIGN KEY({name}) REFERENCES {table}({owner})'.format(
            name=column_name, table=table_name, owner=owner_column, fullname=column_full_name.replace('.', '_'))


class Sqlite(Sql):
    primary_key = 'PRIMARY KEY'

    @staticmethod
    def default(args):
        return f'DEFAULT {args}'

    @staticmethod
    def foreignkey(column_name, table_name, owner_column, column_full_name):
        return 'FOREIGN KEY({name}) REFERENCES {table}({owner})'.format(
            name=column_name, table=table_name, owner=owner_column)


class mysql(Sql):
    pass


class mariadb(mysql):
    pass


class postgresql(Sql):
    pass
