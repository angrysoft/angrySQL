from urllib.parse import urlparse


class Connection:
    def __new__(cls, url, echo=False):
        info = urlparse(url)
        if info.scheme == 'sqlite':
            path = info.path
            if info.hostname:
                path = info.hostname + info.path
            from .sqlite import SqliteConnection
            return SqliteConnection(dbfile=path, echo=echo)
        elif info.scheme == 'mariadb':
            from .mysql import MariaConnection
            return MariaConnection(user=info.username, password=info.password, host=info.hostname, dbname=info.path, port=info.port, echo=echo)