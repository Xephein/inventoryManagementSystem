from cs50 import SQL
from datetime import date
import time

def csvRead(delimiter, filePath, enc):
    with open(filePath, 'r', encoding=enc) as inputFile:
        content = []
        c = 0
        for row in inputFile:
            row = row.replace('\n','')
            row = row.replace('\r','')
            if c == 0:
                headers = row.split(delimiter)
                c += 1
            else:
                tempDict = {}
                row = row.split(delimiter)
                rowc = 0
                for col in headers:
                    tempDict[col] = row[rowc]
                    rowc += 1
                content.append(tempDict)
    return content


today = date.today()
db = SQL("sqlite:///data/ims.db")

ITEMS = db.execute("SELECT * FROM items")

MEMBERS = db.execute("SELECT * FROM members")

rows = db.execute("SELECT * FROM members")

a = time.time()
availableItems = db.execute("SELECT borrows.member_id, members.member_name, members.telephone, borrows.item_id, items.item_name, borrows.start_date, borrows.plan_date \
                            FROM borrows\
                            INNER JOIN members ON borrows.member_id=members.id \
                            INNER JOIN items ON borrows.item_id=items.id \
                            WHERE end_date IS NULL")
b = time.time()

print(availableItems, b - a)
startDate = "2023-11-22"
print(db.execute("SELECT * FROM borrows WHERE start_date <= ? AND plan_date >= ?", startDate, startDate))
print(db.execute("SELECT * FROM borrows WHERE item_id = 4 AND end_date IS NULL AND start_date BETWEEN '2023-11-18' AND '2023-11-21'"))
print(date(today.year, today.month, today.day + 1))

print(db.execute("SELECT * FROM items"))

# content = csvRead(',', "data/members.csv", "utf-8")