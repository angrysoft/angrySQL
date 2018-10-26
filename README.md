# angrySQL
 Simple Sql helper inspired by sqlalchemy but much simpler

## dependecies
* [MySQLdb](https://github.com/PyMySQL/mysqlclient-python) 
 
## For now working db engines:
* Mysql
* sqlite3

##  Create models
```python
from angrysql import BaseModel, Column, Integer, String


class Users(BaseModel):
    user_id = Column(Integer(), primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    email = Column(String(255))
    user_info_id = Column(Integer())

```
## Create db connector
```python
from models import *
from angrysql.mysqldb import Connection
config = {'user': 'db_user_name',
          'password': 'db_password',
          'database': 'db_name'}

db = Connection(config, echo=True)

db.create_tables(Users)

user = db.select(Users).get(3)
if user:
    print(user.login)

users = db.select(Users).all()
for u in users:
    print(u.user_id, u.login)

user = db.select(Users).first()
if user:
    print(user)
    
count = db.delete(Users).all()
print(f'Delete {count} users')
db.commit()

u = Users()
u.login='sebastian'
u.password='ldfjkladfjaljf'
db.insert(u)
db.commit()

```
