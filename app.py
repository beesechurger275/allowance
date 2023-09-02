from db import db
from sqlsafe import sqlsafe, sqlsafeint, sqlsafefloat
from flask import Flask, render_template, session, request, redirect, url_for, abort, flash
import init_db
import hashlib
from sqlite3 import OperationalError
import etc

# TODO admin password changes

database = db()
database.connect("data.sql")

init_db.init_db(database)

app = Flask(__name__)

with open("secretkey.txt", 'r') as key:
    app.secret_key = key.read()
    key.close()

etc.updateWeekly()


@app.route("/")
def index():
    etc.updateWeekly()
    if 'username' not in session:
        return redirect(url_for('login'))

    this_db = db()
    this_db.connect("data.sql")
    account = {}
    account["username"] = session['username']

    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(account["username"])}';
    """

    admin = this_db.readOne(query)
    account["administrator"] = admin[0]

    query = f"""
        SELECT id FROM users WHERE name='{sqlsafe(account["username"])}';
    """

    userId = this_db.readOne(query)
    account["id"] = userId[0]

    query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_to={account["id"]};
    """

    transactionsTo = this_db.read(query)

    query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from={account["id"]};
    """

    transactionsFrom = this_db.read(query)

    add = transactionsTo[0][0]
    if add == None:
        add = 0
    sub = transactionsFrom[0][0]
    if sub == None:
        sub = 0

    account["balance"] = round(add - sub, 2)

    this_db.close()

    return render_template("index.html", account=account)


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    etc.updateWeekly()
    if request.method == "GET":
        try:
            username = session['username']
        except KeyError:
            return redirect(url_for('login'))

        this_db = db()
        this_db.connect("data.sql")
        account = {} 
        account["username"] = username

        query = f"""
            SELECT id FROM users WHERE name='{sqlsafe(account["username"])}';
        """

        userId = this_db.readOne(query)
        account["id"] = userId[0]

        query = f"""
            SELECT SUM(transferamount) FROM transactions WHERE user_id_to={account["id"]};
        """

        transactionsTo = this_db.read(query)
        add = transactionsTo[0][0]
        if add == None:
            add = 0
        
        query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from={account["id"]};
        """

        transactionsFrom = this_db.read(query)
        sub = transactionsFrom[0][0]
        if sub == None:
            sub = 0

        account["balance"] = round(add - sub, 2)


        return render_template("transfer.html", account=account)

    if 'username' in session:
        username = session['username']
    else:
        return redirect(url_for('login'))
    
    if request.form["name"] == "" or request.form["amount"] == "":
        flash("You need to fill in the form completely!")
        return redirect(url_for("transfer"))
    if float(request.form["amount"]) <= 0:
        flash("Nice try. Enter a number above 0")
        return redirect(url_for("transfer"))

    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT id FROM users WHERE name='{sqlsafe(username)}';
    """

    q = this_db.readOne(query)
    fromid = q[0]

    balance = 0

    q = f"""
    SELECT SUM(transferamount) FROM transactions WHERE user_id_to='{fromid}';
    """
    h = this_db.read(q)
    add = h[0][0]
    if add == None:
        add = 0

    q = f"""
    SELECT SUM(transferamount) FROM transactions WHERE user_id_from='{fromid}';
    """
    h = this_db.read(q)
    sub = h[0][0]
    if sub == None:
        sub = 0

    balance = round(add - sub, 2)

    if balance - float(request.form["amount"]) < 0:
        flash("You can't transfer more than you have!")
        return redirect(url_for("transfer"))

    query = f"""
    SELECT id FROM users WHERE name='{sqlsafe(request.form["name"])}'
    """

    q = this_db.readOne(query)
    try:
        toid = q[0]
    except TypeError:
        flash("Enter valid username!")
        return redirect(url_for("transfer"))

    if fromid == toid:
        flash("You can't transfer to yourself!")
        return redirect(url_for("transfer"))

    query = f"""
    INSERT INTO transactions (transferamount, user_id_to, user_id_from) VALUES ({sqlsafefloat(request.form["amount"])}, {toid}, {fromid}); 
    """

    this_db.execute(query)

    this_db.close()

    flash("Transfer complete!")
    return redirect(url_for("transfer"))


@app.route("/viewaccounts")
def viewall():
    etc.updateWeekly()
    if 'username' not in session:
        return redirect(url_for('login'))
        
    this_db = db()
    this_db.connect("data.sql")
    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(session['username'])}'
    """
    isAdmin = this_db.readOne(query)[0]
    if not isAdmin:
        return redirect(url_for("index"))
    query = """
    SELECT id FROM users ORDER BY id;
    """
    userids = this_db.read(query)
    bals = {}

    query = f"""
    SELECT name FROM users ORDER BY id;
    """
    usernames = this_db.read(query)
    for id in userids:
        a = id[0]
        query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_to='{a}';
        """
        plus = this_db.readOne(query)[0]
        query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from='{a}';
        """
        minus = this_db.readOne(query)[0]
        if plus == None:
            plus = 0
        if minus == None:
            minus = 0
        bals[a] = plus - minus
        
    query = f"""
    SELECT date FROM updates ORDER BY id DESC LIMIT 1;
    """
    lastweekly = etc.getDate(this_db.readOne(query)[0])
    return render_template("viewaccounts.html", bals=bals, usernames=usernames, lastweekly=lastweekly)



@app.route("/adminpasswordchange/<name>", methods=["GET", "POST"])
def adminpasswordchange(name):
    if 'username' not in session:
        return redirect(url_for('login'))

    this_db = db()
    this_db.connect("data.sql")
    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(session['username'])}'
    """
    isAdmin = this_db.readOne(query)[0]
    if not isAdmin:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("adminpasswordchange.html", user=name)
    
    adminHash = hashlib.sha256(bytes(request.form['admin'], "utf-8")).hexdigest()
    getPass = f"""
    SELECT hash FROM users WHERE name='{session['username']}'
    """
    storedPass = this_db.readOne(getPass)[0]

    if request.form["new"] == '' or request.form["confirm"] == '' or request.form["admin"] == '':
        flash("Fill out form completely!")
        return render_template("account.html")

    if adminHash != storedPass:
        flash("Password change failed! Admin password incorrect!")
        return render_template('adminpasswordchange.html', user=name)

    if request.form['new'] == request.form["confirm"]:
        print('passwords match')

        passHash = hashlib.sha256(bytes(request.form['new'], "utf-8")).hexdigest()

        query = f"""
        UPDATE users SET hash='{sqlsafe(passHash)}' WHERE name='{sqlsafe(name)}';
        """

        this_db.execute(query)

        flash("Password change complete!")
        return render_template('adminpasswordchange.html', user=name)
    
    flash("Password change failed! Passwords do not match!")
    return render_template('adminpasswordchange.html', user=name)
        
        

@app.route("/accounts/<name>")
def individualaccount(name):
    etc.updateWeekly()
    if 'username' not in session:
        return redirect(url_for('login'))
    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(session['username'])}'
    """

    isAdmin = this_db.readOne(query)[0]
    if not isAdmin:
        if name != session['username']:
            return redirect(url_for("index"))

    account = {}
    transactions = []
    account['username'] = sqlsafe(name)
    
    query = f"""
    SELECT id FROM users WHERE name="{account['username']}"
    """
    account['id'] = this_db.read(query)[0][0]

    query = f"""
    SELECT SUM(transferamount) FROM transactions WHERE user_id_to='{account['id']}';
    """
    add = this_db.readOne(query)[0]
    if add == None:
        add = 0

    query = f"""
    SELECT SUM(transferamount) FROM transactions WHERE user_id_from='{account['id']}';
    """
    sub = this_db.readOne(query)[0]
    if sub == None:
        sub = 0

    account['balance'] = add - sub

    query = f"""
    SELECT birthdate FROM users WHERE id='{account['id']}';
    """

    account['birthdate'] = this_db.readOne(query)[0]

    query = f"""
    SELECT * FROM transactions WHERE user_id_to={account['id']} OR user_id_from='{account['id']}'
    """
    transactionsQ = this_db.read(query) # 0=id, 1=amount, 2=user_id_to, 3=user_id_from, 4=timestamp, 5=usertofrom

    for transaction in transactionsQ:
        transactionList = list(transaction)

        if transaction[2] == account['id']: # to this account 
            query = f"""
            SELECT user_id_from FROM transactions WHERE id={transaction[0]}
            """
        else: # from this account
            query = f"""
            SELECT user_id_to FROM transactions WHERE id={transaction[0]}
            """

        tofrom = this_db.readOne(query)[0]
        query = f"""
        SELECT name FROM users WHERE id={tofrom}
        """

        try:
            usertofrom = this_db.readOne(query)[0]
        except OperationalError:
            usertofrom = "admintransfer" # No user_id_from
        transactionList.append(usertofrom)
        transactions.append(transactionList)


    return render_template("viewaccount.html", account=account, transactions=transactions, admin=isAdmin)
    

@app.route("/adminpanel/", methods=["GET", "POST"])
def adminpanel():
    etc.updateWeekly()
    if 'username' not in session:
        return redirect(url_for('login'))
    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(session['username'])}'
    """

    isAdmin = this_db.readOne(query)[0]
    if not isAdmin:
        return redirect(url_for("index"))

    if request.method == "GET":
        return render_template("adminpanel.html")
    
    if request.form["name"] == "" or request.form["amount"] == "":
        flash("You need to fill in the form completely!")
        return redirect(url_for("transfer"))    

    query = f"""
    SELECT id FROM users WHERE name='{sqlsafe(request.form["name"])}'
    """

    idq = this_db.readOne(query)

    try:
        toid = idq[0]
    except TypeError:
        flash("Invalid user!")
        return redirect(url_for("adminpanel"))
    
    query = f"""
    INSERT INTO transactions (transferamount, user_id_to) VALUES ({sqlsafefloat(request.form["amount"])}, {toid});
    """

    this_db.execute(query)

    flash("Transfer complete!")
    return redirect(url_for("adminpanel"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'username' not in session:
            return render_template("login.html")
        return redirect(url_for("index"))
        
    try:
        test = session['username'] # pain
        test = None
        return redirect(url_for('index'))
    except KeyError:
        pass

    this_db = db()
    this_db.connect("data.sql")

    if request.form['username'] == '' or request.form['password'] == '':
        flash("Enter both username and password!")
        this_db.close()
        return redirect(url_for("login"))

    query = f"""
        SELECT hash FROM users WHERE name='{request.form['username']}';
        """
    try:
        q = this_db.readOne(query)
        hashCheck = q[0]
        passHash = hashlib.sha256(bytes(request.form["password"], "utf-8")).hexdigest()
    except TypeError:
        flash("Username or password incorrect!")
        this_db.close()
        return redirect(url_for("login"))

    if passHash != hashCheck:
        flash("Username or password incorrect!")
        this_db.close()
        return redirect(url_for("login"))

    session['username'] = request.form['username']
    return redirect(url_for("index"))


@app.route("/addaccount", methods=['GET', 'POST'])
def addaccount():
    etc.updateWeekly()

    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT administrator FROM users WHERE name='{sqlsafe(session['username'])}'
    """

    isAdmin = this_db.readOne(query)[0]
    if not isAdmin:
        return redirect(url_for("index"))
    
    if request.method == 'GET':
        return render_template("create.html")
    

    username = sqlsafe(request.form['username'])
    if username == None:
        flash("Username not entered!")
        return redirect(url_for("addaccount"))
    
    password = hashlib.sha256(bytes(request.form["password"], "utf-8")).hexdigest()
    password2 = hashlib.sha256(bytes(request.form["confirm"], "utf-8")).hexdigest()

    if password == None:
        flash("Enter password!")
        return redirect(url_for("addaccount"))
    
    if password != password2:
        flash("Passwords do not match!")
        return redirect(url_for("addaccount"))
    
    if 'admin' in request.form:
        if request.form['admin'] == "on":
            admin = 1
        else:
            admin = 0
    else:
        admin = 0

    birthdate = sqlsafe(request.form['birthdate'])

    if birthdate == '':
        birthdate = 'NULL'
    else:
        birthdate = etc.getDate(birthdate)

    query = f"""
    INSERT INTO users(name, hash, administrator, birthdate) VALUES ('{username}', '{password}', {admin}, '{birthdate}');
    """

    this_db.execute(query)

    flash("User creation successful!")
    return redirect(url_for("addaccount"))


@app.route("/account", methods=["GET", "POST"])
def account():
    etc.updateWeekly()
    if request.method == "GET":
        if 'username' in session:
            return render_template("account.html")
        return redirect(url_for("login"))
    

    if request.form["current"] == '' or request.form["new"] == '' or request.form["confirm"] == '':
        flash("Fill out form completely!")
        return render_template("account.html")

    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT hash FROM users WHERE name='{session["username"]}';
    """
    read = this_db.readOne(query)
    current = read[0]

    currentForm = hashlib.sha256(bytes(request.form['current'], "utf-8")).hexdigest()

    new = hashlib.sha256(bytes(request.form['new'], "utf-8")).hexdigest()
    confirm = hashlib.sha256(bytes(request.form['confirm'], "utf-8")).hexdigest()

    if currentForm != current:
        flash("Current password incorrect")
        return render_template("account.html")

    if new != confirm:
        flash("Passwords do not match")
        return render_template("account.html")

    query = f"""
    UPDATE users SET hash='{new}' WHERE name='{session['username']}';
    """

    this_db.execute(query)

    flash("Password change complete!")
    return render_template("account.html")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))


@app.errorhandler(404)
def not_found(a):
    return "Error 404"


@app.errorhandler(500)
def fivehundred(a):
    return "Error 500"

if __name__ == "__main__":
    app.run(host='0.0.0.0')