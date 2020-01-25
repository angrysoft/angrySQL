#!/usr/bin/python

from angrysql import Connection
from angrysql import BaseModel
from angrysql import Column, Integer, String, SmallInteger, TinyInteger, Year, TimeStamp
from angrysql.base import Insert
from hashlib import sha256
import unittest


class Users(BaseModel):
    user_id = Column(Integer(), primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(), nullable=False)
    email = Column(String(255))


class UserRates(BaseModel):
    rate_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, foreignkey='users.user_id')
    rate_name_id = Column(Integer(), nullable=False, foreignkey='rate_name.rate_name_id')
    value = Column(SmallInteger(), default='0')


class RateName(BaseModel):
    rate_name_id = Column(Integer(), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)


class Addons(BaseModel):
    user_addon_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, foreignkey='users.user_id')
    rate_name_id = Column(Integer(), nullable=False, foreignkey='rate_name.rate_name_id')
    work_days_id = Column(Integer(), nullable=False, foreignkey='work_days.work_days_id')
    value = Column(SmallInteger(), default='0')


class WorkDays(BaseModel):
    work_days_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, foreignkey='users.user_id')
    day = Column(TinyInteger(zerofill=True), nullable=False)
    month = Column(TinyInteger(zerofill=True), nullable=False)
    year = Column(Year(), nullable=False)
    start = Column(TimeStamp(), nullable=False)
    end = Column(TimeStamp(), nullable=False)
    user_rate_id = Column(Integer(), foreignkey='user_rates.rate_id')
    

class TestDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Connection('sqlite://test.db', echo=True)
        
    def test_a_creeate_tables(self):
        self.assertIsNone(self.db.create_tables(Users, UserRates, RateName, Addons, WorkDays))
        
    def test_b_insert(self):
        for i in range(0,100):
            u = Users(login=f'user_{i:02}', password=sha256(f'user_{i}'.encode()).hexdigest(), email=f'user_{i}@test.org')
            self.assertIsInstance(self.db.insert(u), Insert)
    
    def test_c_commit(self):
        self.db.commit()
    
    def test_d_select_byid(self):
        u = self.db.select(Users).get(3)
        print(u)
        self.assertIsInstance(u, Users)
    
    def test_d_select_one(self):
        u = self.db.select(Users).one()
        print(u)
        self.assertIsInstance(u, Users)
    
    def test_d_select_all(self):
        u = self.db.select(Users).all()
        for i in u:
            print(i)
        self.assertIsInstance(u, list)
    
    def test_d_select_all_order(self):
        u = self.db.select(Users).order_by(Users.login, desc=True).all()
        for i in u:
            print(i)
        self.assertIsInstance(u, list)
    
    def test_e_select_where(self):
        u = self.db.select(Users).where(Users.login == 'user_99').all()
        print(u)
        self.assertIsInstance(u, list)
        
    

if __name__ == "__main__":
    unittest.main()