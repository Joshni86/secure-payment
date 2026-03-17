import sqlite3
conn=sqlite3.connect("payment.sqlite")
cursor=conn.cursor()
create_query="""CREATE TABLE IF NOT EXISTS Users (id integer primary key autoincrement, email text not null unique, password text not null, balance double DEFAULT 0.0)"""

create_transaction="""
CREATE TABLE IF NOT EXISTS Transactions
(id integer primary key, user_id integer not null,amount double not null,currency text not null,merchant_id integer not null,foreign key(user_id) references Users(id)
"""
alter_trans="""
CREATE TABLE Transactions (
    id integer primary key,
    user_id integer not null,
    amount double not null,
    currency text not null,
    merchant_id integer not null,
    pay_hash text unique not null,
    foreign key(user_id) references Users(id)
)
"""
cursor.execute(create_query)
cursor.execute(alter_trans)
conn.close()