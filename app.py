from cs50 import SQL
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for
import util
import webbrowser


# Validation Functions
def startDateHistoric(startDate):
    if date.fromisoformat(startDate) < date.today():
        return True
    return False

def startDateInterrupts(startDate, itemID):
    if [] != db.execute("SELECT * FROM borrows WHERE start_date < ? AND plan_date > ? AND item_id = ? AND end_date IS NULL", startDate, startDate, itemID):
        return True
    return False
    
def startDateOverlaps(startDate, itemID):
    return db.execute("SELECT * FROM borrows WHERE plan_date = ? AND item_id = ? AND end_date IS NULL", startDate, itemID)
    
def planDateEarlierThanStart(startDate, endDate):
    if date.fromisoformat(endDate) < date.fromisoformat(startDate):
        return True
    return False

def borrowPeriodsMatch(startDate, planDate, itemID):
    if [] != db.execute("SELECT * FROM borrows WHERE start_date = ? AND plan_date = ? AND item_id = ? and end_date is NULL", startDate, planDate, itemID):
        return True
    return False

def borrowPeriodOverlaps(startDate, planDate, itemID):
    if [] != db.execute("SELECT * FROM borrows WHERE start_date > ? AND start_date < ? AND item_id = ? AND end_date IS NULL", startDate, planDate, itemID):
        return True
    return False

def planDateOverlaps(planDate, itemID):
    return db.execute("SELECT * FROM borrows WHERE start_date = ? AND item_id = ? and end_date IS NULL", planDate, itemID)


# General Functions
def getID(nameInput):
    return int(nameInput[0:nameInput.find('.')])

def csvRead(input, delimiter, enc):
    content = []
    c = 0
    for row in input:
        row = row.decode(enc, "ignore")
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

def csvWrite(name, content):
    headers = list(content[0].keys())
    data = ",".join(headers)
    data += "\n"
    for dicts in content:
        for key in dicts:
            dicts[key] = str(dicts[key])
    for dictionary in content:
        row = ",".join(list(dictionary.values()))
        data += row + "\n"
    f = open("data/" + name + ".csv", "w")
    f.write(data)
    f.close()

# Database Call Functions (eventually seperate file)
def getMembersWithBorrows():
    return db.execute("SELECT * FROM members WHERE id IN \
                    (SELECT member_id FROM borrows WHERE end_date IS NULL)")

def getEntriesAll(table):
    return db.execute("SELECT * FROM ?", table)

def getEntryByID(table, ident):
    return db.execute("SELECT * FROM ? WHERE id = ?", table, ident)

def deleteEntry(table, ident):
    return db.execute("DELETE FROM ? WHERE id = ?", table, ident)

def getBorrowsReadable():
    return db.execute("SELECT borrows.id, borrows.member_id, members.member_name, borrows.item_id, items.item_name, borrows.start_date, borrows.plan_date, borrows.end_date \
                            FROM borrows\
                            INNER JOIN members ON borrows.member_id=members.id \
                            INNER JOIN items ON borrows.item_id=items.id")

def getBorrowsRelated(ident):
    return db.execute("SELECT borrows.id, borrows.member_id, members.member_name, borrows.item_id, items.item_name, borrows.start_date, borrows.plan_date, borrows.end_date \
                            FROM borrows\
                            INNER JOIN members ON borrows.member_id=members.id \
                            INNER JOIN items ON borrows.item_id=items.id WHERE member_id = ? AND end_date IS NULL", ident)

def getOngoingBorrows():
    return db.execute("SELECT borrows.member_id, members.member_name, members.telephone, borrows.item_id, items.item_name, borrows.start_date, borrows.plan_date \
                            FROM borrows\
                            INNER JOIN members ON borrows.member_id=members.id \
                            INNER JOIN items ON borrows.item_id=items.id \
                            WHERE end_date IS NULL\
                            ORDER BY start_date")

app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=False)

webbrowser.open("http://127.0.0.1:5000")

# Establish database connection and query items and members in database:
db = SQL("sqlite:///data/ims.db")

ITEMS = getEntriesAll("items")
MEMBERS = getEntriesAll("members")
DAYLIMIT = 1

ITEMNAMES = []

# Rendering of webpages:
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/borrow", methods=["GET", "POST"])
def imsborrow():
    today = date.today()
    limitdate = today + timedelta(days=DAYLIMIT)

    availableItems = db.execute("SELECT id, item_name FROM items WHERE id NOT IN \
                      (SELECT item_id FROM borrows WHERE end_date IS NULL AND start_date <= ?)", str(date(limitdate.year, limitdate.month, limitdate.day)))
    
    borrowsOngoing = getOngoingBorrows()
    
    categories = db.execute("SELECT category FROM items GROUP BY category")

    return render_template("borrow.html",
                           members=MEMBERS,
                           items=availableItems,
                           bStuff=borrowsOngoing,
                           today=date.today(),
                           categories=categories)

@app.route("/borrow/form", methods=["POST"])
def borrowform():
    ## Information
    today = date.today()
    limitdate = today + timedelta(days=DAYLIMIT)

    availableItems = db.execute("SELECT id, item_name FROM items WHERE id NOT IN \
                      (SELECT item_id FROM borrows WHERE end_date IS NULL AND start_date <= ?)", str(date(limitdate.year, limitdate.month, limitdate.day)))
    
    borrowsOngoing = getOngoingBorrows()
    
    categories = db.execute("SELECT category FROM items GROUP BY category")

    ## Borrowing

    # Prepare for validation:
    membernames = []
    for member in MEMBERS:
        membernames.append(member["member_name"])

    
    for item in ITEMS:
        ITEMNAMES.append(item["item_name"])

    # Get inputs from html form:
    nameID = getID(request.form.get("name"))
    name = getEntryByID("members", nameID)[0]["member_name"]
    
    itemID = getID(request.form.get("item"))
    itemName = getEntryByID("items", itemID)[0]["item_name"]

    startDate = request.form.get("startDate")
    planDate = request.form.get("planDate")

    # Validations:
    
    planDateOverlapsData = planDateOverlaps(planDate, itemID)
    startDateOverlapsData = startDateOverlaps(startDate, itemID)

    if name not in membernames:
        return render_template("borrow.html",
                                alert=util.memberError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif itemName not in ITEMNAMES:
        return render_template("borrow.html",
                                alert=util.itemError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif startDateHistoric(startDate):
        return render_template("borrow.html",
                                alert=util.startDateHistoricError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif planDateEarlierThanStart(startDate, planDate):
        return render_template("borrow.html",
                                alert=util.planDateEarlierError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif borrowPeriodsMatch(startDate, planDate, itemID):
        return render_template("borrow.html",
                                alert=util.borrowPeriodsMatchError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif startDateInterrupts(startDate, itemID):
        return render_template("borrow.html",
                                alert=util.startDateInterruptError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif borrowPeriodOverlaps(startDate, planDate, itemID):
        return render_template("borrow.html",
                                alert=util.borrowsOverlapError,
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif startDateOverlapsData != []:
        db.execute("INSERT INTO borrows (member_id, item_id, start_date, plan_date) VALUES(?, ?, ?, ?)",
                nameID, itemID, startDate, planDate)
        borrowsOngoing = getOngoingBorrows()
        return render_template("borrow.html",
                                alert=util.startDateOverlapAlert,
                                interrupted=getEntryByID("members", startDateOverlapsData[0]["member_id"]),
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    
    elif planDateOverlapsData != []:
        db.execute("INSERT INTO borrows (member_id, item_id, start_date, plan_date) VALUES(?, ?, ?, ?)",
                nameID, itemID, startDate, planDate)
        borrowsOngoing = getOngoingBorrows()
        return render_template("borrow.html",
                                alert=util.planDateOverlapAlert,
                                interrupted=getEntryByID("members", planDateOverlapsData[0]["member_id"]),
                                members=MEMBERS,
                                items=availableItems,
                                bStuff = borrowsOngoing,
                                categories=categories,
                                today=today)
    

    
    # If good insert into borrows
    db.execute("INSERT INTO borrows (member_id, item_id, start_date, plan_date) VALUES(?, ?, ?, ?)",
                nameID, itemID, startDate, planDate)
    
    return redirect("/borrow")

@app.route("/borrow/category", methods = ["POST"])
def borrowcategory():
    today = date.today()
    mName = request.form.get("name")
    category = request.form.get("category")

    if category != "":
        itemsFiltered = db.execute("SELECT id, item_name FROM items WHERE category = ? AND id NOT IN \
                                (SELECT item_id FROM borrows WHERE end_date IS NULL AND start_date <= ?)",
                                category, str(date(today.year, today.month, today.day + DAYLIMIT)))
    else:
        itemsFiltered = getEntriesAll("items")

    borrowsOngoing = getOngoingBorrows()
    
    categories = db.execute("SELECT category FROM items GROUP BY category")

    return render_template("borrow.html", members=MEMBERS, items=itemsFiltered, bStuff=borrowsOngoing, today=date.today(), categories=categories, cat=category, name=mName)


@app.route("/return", methods = ["GET", "POST"])
def imsreturn():
    members = getMembersWithBorrows()
    
    return render_template("return.html", members=members)


@app.route("/return/form", methods = ["POST"])
def returnform():
    # Select members with pending borrows:
    members = getMembersWithBorrows()
    
    # create list with member IDs for validation purposes:
    memberIDs = []
    for row in members:
        memberIDs.append(int(row["id"]))

    # Get values from forms:
    selectedName = request.form.get("name")
    memberID = getID(selectedName)
    member = getEntryByID("members", memberID)

    selectedItem = request.form.get("item")
    if selectedItem:
        itemID = getID(selectedItem)
    
    # Validate memberID and create borrowed item list for validation purpose:
    if memberID in memberIDs:
        items = db.execute("SELECT id, item_name FROM items WHERE id IN \
                                (SELECT item_id FROM borrows WHERE member_id = ? AND end_date is NULL)", memberID)
        
        borrowsRelated = getBorrowsRelated(memberID)

        itemIDs = []
        for row in items:
            itemIDs.append(int(row["id"]))

    # if no item specified return page where item is pickable:
    if not selectedItem and memberID in memberIDs:
        return render_template("return.html",
                            name=member[0]["member_name"],
                            members=member,
                            items=items,
                            memberID=memberID,
                            related=borrowsRelated)
    
    # if member and item exist update row with bring back date:
    elif (memberID in memberIDs) and (itemID in itemIDs):
        today = str(date.today())
        borrowID = request.form.get("borrowID")
        db.execute("UPDATE borrows SET end_date = ? WHERE id = ?", today, borrowID)

        members = getMembersWithBorrows()
        borrowsRelated = getBorrowsRelated(memberID)

        return render_template("return.html",
                                name=member[0]["member_name"],
                                members=members,
                                items=items,
                                related=borrowsRelated,
                                memberID=memberID,
                                alert=util.successMessage)
    else:
        return render_template("return.html",
                               alert=util.errorMessage)
    
@app.route("/upload", methods = ["GET", "POST"])
def upload():
    return render_template("upload.html")


@app.route("/upload/form", methods = ["GET", "POST"])
def uploadform():
    inputCSV = request.files["inputFile"]
    enc = request.form.get("encoding")
    delimiter = request.form.get("delimiter")
    table = request.form.get("table")
    content = csvRead(inputCSV, delimiter, enc)
    columns = list(content[0].keys())
    for row in content:
        if table == "members":
            db.execute("INSERT INTO ? (?, ?) VALUES (?, ?)", table, columns[0], columns[1], row[columns[0]], row[columns[1]])
        elif table == "items":
            db.execute("INSERT INTO ? (?, ?, ?) VALUES (?, ?, ?)", table, columns[0], columns[1], columns[2], row[columns[0]], row[columns[1]], row[columns[2]])
        else:
            return "Table does not exist."

    return redirect("/upload")


@app.route("/admin", methods = ["GET", "POST"])
def admin():
    return render_template("admin.html")

@app.route("/admin/members", methods = ["GET", "POST"])
def adminMembers():
    memberList = getEntriesAll("members")
    return render_template("adminmembers.html", members=memberList)

@app.route("/admin/items", methods = ["GET", "POST"])
def adminItems():
    itemList = getEntriesAll("items")
    return render_template("adminitems.html", items=itemList)

@app.route("/admin/borrows", methods = ["GET", "POST"])
def adminBorrows():
    borrowList = getBorrowsReadable()
    return render_template("adminborrows.html", borrows=borrowList)

@app.route("/admin/handler", methods = ["POST"])
def adminHandler():
    mode = request.form.get("mode")
    if mode == "members":
        deleteEntry("members", request.form.get("memberID"))
        global MEMBERS
        MEMBERS = getEntriesAll("members")
        return redirect(url_for("adminMembers"), code=307)
    elif mode == "items":
        deleteEntry("items", request.form.get("itemID"))
        return redirect(url_for("adminItems"), code=307)
    elif mode =="borrows":
        deleteEntry("borrows", request.form.get("borrowID"))
        return redirect(url_for("adminBorrows"), code=307)
    else:
        return "You have reached places no man has gone before"
    
@app.route("/admin/editor", methods=["POST"])
def adminEditor():
    mode = request.form.get("mode")

    if mode == "members":
        memberToEdit = getEntryByID(mode, request.form.get("memberID"))[0]
        return render_template("admineditor.html", mode=mode, member=memberToEdit)
    
    elif mode == "items":
        itemToEdit = getEntryByID(mode, request.form.get("itemID"))[0]
        return render_template("admineditor.html", mode=mode, item=itemToEdit)
    
    elif mode == "borrows":
        borrowToEdit = getEntryByID(mode, request.form.get("borrowID"))[0]
        return render_template("admineditor.html", mode=mode, borrow=borrowToEdit)
     
    elif mode == "update":
        table = request.form.get("table")
        if table == "members":
            db.execute("UPDATE members SET member_name = ?, telephone = ? WHERE id = ?",
                        request.form.get("memberName"),
                        request.form.get("telephone"),
                        request.form.get("memberID"))
            return redirect(url_for("adminMembers"), code=307)
        
        elif table == "items":
            db.execute("UPDATE items SET item_name = ?, category = ? WHERE id = ?",
                        request.form.get("itemName"),
                        request.form.get("category"),
                        request.form.get("itemID"))
            return redirect(url_for("adminItems"), code=307)
        
        elif table == "borrows":
            return
        
    else:
        return "Stay away from withcraft, User, for this is my final warning!"
    
@app.route("/admin/toggle", methods=["POST"])
def adminToggle():
    mode = request.form.get("mode")
    if mode == "members":
        memberID = request.form.get("memberID")
        memberToToggle = getEntryByID(mode, memberID)
        if memberToToggle[0]["can_borrow"] == 1:
            db.execute("UPDATE members SET can_borrow = 0 WHERE id = ?", memberID)
        else:
            db.execute("UPDATE members SET can_borrow = 1 WHERE id = ?", memberID)
        global MEMBERS
        MEMBERS = getEntriesAll("members")

        return render_template("adminmembers.html", members=MEMBERS)

    elif mode == "items":
        itemID = request.form.get("itemID")
        itemToToggle = getEntryByID(mode, itemID)
        if itemToToggle[0]["can_be_borrowed"] == 1:
            db.execute("UPDATE items SET can_be_borrowed = 0 WHERE id = ?", itemID)
        else:
            db.execute("UPDATE items SET can_be_borrowed = 1 WHERE id = ?", itemID)
        global ITEMS
        ITEMS = getEntriesAll("items")

        return render_template("adminitems.html", items=ITEMS)
    
    
@app.route("/admin/insert", methods=["POST"])
def adminInsert():
    mode = request.form.get("mode")
    if mode == "memberInsert":
        newName = request.form.get("newName")
        newContact = request.form.get("newContact")
        db.execute("INSERT INTO members (member_name, telephone) VALUES (?, ?)",
                    newName,
                    newContact)
        global MEMBERS
        MEMBERS = getEntriesAll("members")
        return redirect(url_for("adminMembers"), code=307)
    elif mode == "itemInsert":
        newName = request.form.get("newName")
        newCategory = request.form.get("newCategory")
        newDescription = request.form.get("newDescription")
        db.execute("INSERT INTO items (item_name, category, description) VALUES (?, ?, ?)",
                    newName,
                    newCategory,
                    newDescription)
        global ITEMS
        ITEMS = getEntriesAll("items")
        return redirect(url_for("adminItems"), code=307)
    else:
        return "I have warned you before, User. Make sure to not regret the consequences of your actions."
    
@app.route("/download/members", methods=["POST"])
def downloadMembers():
    content = getEntriesAll("members")
    csvWrite("memberExport", content)

    return redirect(url_for("upload"))

@app.route("/download/items", methods=["POST"])
def downloadItems():
    content = getEntriesAll("items")
    csvWrite("itemExport", content)

    return redirect(url_for("upload"))


app.route("/admin/override", methods=["POST"])
def overrideDatabase():
    inputCSV = request.files["inputFile"]
    