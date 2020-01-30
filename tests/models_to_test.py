from angrysql import BaseModel
from angrysql import Column, Integer, String, SmallInteger, TinyInteger, Year, TimeStamp

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