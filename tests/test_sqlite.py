#!/usr/bin/python

from angrysql import Connection
from angrysql.base import Insert
from hashlib import sha256
from .models_to_test import *
import unittest


def tprint(msg):
    print(f'\t{msg}')

class TestSqlite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Connection('sqlite://test.db', echo=True)
        
    def test_a_creeate_tables(self):
        self.assertIsNone(self.db.create_tables(Users, UserRates, RateName, Addons, WorkDays))
        
    def test_b_insert(self):
        for i in range(0,100):
            u = Users(login=f'user_{i:02}', password=sha256(f'user_{i}'.encode()).hexdigest(), email=f'user_{i}@test.org')
            ret = self.db.insert(u).do()
            print(ret)
            self.assertIsInstance(ret , int)
    
    def test_c_commit(self):
        self.db.commit()
    
    def test_d_select_byid(self):
        u = self.db.select(Users).get(3)
        tprint(u)
        self.assertIsInstance(u, Users)
    
    def test_d_select_one(self):
        u = self.db.select(Users).one()
        tprint(u)
        self.assertIsInstance(u, Users)
    
    def test_d_select_all(self):
        u = self.db.select(Users).all()
        for i in u:
            tprint(i)
        self.assertIsInstance(u, list)
    
    def test_d_select_all_order(self):
        u = self.db.select(Users).order_by(Users.login, desc=True).all()
        for i in u:
            tprint(i)
        self.assertIsInstance(u, list)
    
    def test_e01_select_where(self):
        u = self.db.select(Users).where(Users.login == 'user_99').all()
        tprint(u)
        self.assertIsInstance(u, list)
    
    def test_e02_select_login(self):
        u = self.db.select(Users).columns(Users.login).where(Users.user_id < 10).all()
        for i in u:
            tprint(i.login)
            tprint(i.email)
        self.assertIsInstance(u, list)
    
    def test_e03_select_like(self):
        u = self.db.select(Users).where(Users.login.like('user_0_')).all()
        for i in u:
            tprint(i.login)
            tprint(i.email)
        self.assertIsInstance(u, list)
    
    def test_e04_select_in(self):
        u = self.db.select(Users).where(Users.login.in_('user_01', 'user_03', 'user_05')).all()
        for i in u:
            tprint(i.login)
            tprint(i.email)
        self.assertIsInstance(u, list)
        
    def test_e05_select_not_in(self):
        u = self.db.select(Users).where(Users.login.not_in('user_01', 'user_03', 'user_05')).all()
        for i in u:
            tprint(i.login)
            tprint(i.email)
        self.assertIsInstance(u, list)
        
    def test_e06_select_between(self):
        u = self.db.select(Users).where(Users.user_id.between(95, 99)).all()
        for i in u:
            tprint(f"{i.login} {i.user_id}")
        self.assertIsInstance(u, list)
    
    def test_e07_delete_where(self):
        u = self.db.delete(Users).where(Users.user_id > 10).do()
        tprint(u)
        self.assertIsInstance(u, int)
    
        
    

if __name__ == "__main__":
    unittest.main()