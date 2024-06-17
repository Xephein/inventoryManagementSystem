#Inventory Management System

This coding project was made to make a borrowing system possible for most any items.

It uses 3 datatables to store information on people who would like to borrow items (members), the items which can be borrowed (items) and the record of historical and planned borrows (borrows).

Databases are wiped to ensure no privacy issues.

##Database schema:

CREATE TABLE members(
id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
member_name TEXT NOT NULL,
telephone TEXT NOT NULL,
can_borrow INTEGER DEFAULT "1" NOT NULL
);

CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE items(
id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
inventory_id TEXT,
item_name TEXT NOT NULL,
category TEXT NOT NULL,
description TEXT,
can_be_borrowed INTEGER DEFAULT "1" NOT NULL
);

CREATE TABLE borrows(
id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
member_id INTEGER NOT NULL,
item_id INTEGER NOT NULL,
start_date NUMERIC NOT NULL,
plan_date NUMERIC NOT NULL,
end_date NUMERIC,
FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE,
FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE
);
