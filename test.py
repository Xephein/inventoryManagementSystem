from datetime import date
import time
import sqlite3 as SQL


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

con = SQL.connect("data/ims.db")

cur = con.cursor()

res = cur.execute("SELECT * FROM members")
for row in res:
    print(row)

