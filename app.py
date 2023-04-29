from db import db
from flask import Flask, render_template, session, request, make_response, redirect, url_for, abort, flash
from markupsafe import escape
import init_db
import hashlib

database = db()
database.connect("data.sql")

init_db.init_db(database)

app = Flask(__name__)

with open("secretkey.txt", 'r') as key:
    app.secret_key = key.read()
    key.close()

@app.route("/")
def index():
    try:
        username = session['username']
    except KeyError:
        return redirect(url_for('login'))
    
    this_db = db()
    this_db.connect("data.sql")
    account = {}
    account["username"] = username
    
    query = f"""
    SELECT administrator FROM users WHERE name='{account["username"]}'
    """

    admin = this_db.readOne(query)
    account["administrator"] = admin[0]

    query = f"""
        SELECT id FROM users WHERE name='{account["username"]}';
    """

    userId = this_db.readOne(query)
    account["id"] = userId[0]

    query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_to={account["id"]};
    """

    transactionsTo = this_db.read(query)
    print(transactionsTo[0][0])

    query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from={account["id"]};
    """

    transactionsFrom = this_db.read(query)

    add = transactionsTo[0][0]
    sub = transactionsFrom[0][0]

    if add != None and sub != None:
        account["balance"] = round(add - sub, 2)
    elif add == None and sub == None:
        account["balance"] = 0
    elif sub == None:
        account["balance"] = round(add, 2)
    elif add == None:
        account["balance"] = round(sub, 2)

    this_db.close()

    return render_template("index.html", account=account)


@app.route("/transfer", methods=["GET", "POST"])
def transfer():
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
            SELECT id FROM users WHERE name='{account["username"]}';
        """

        userId = this_db.readOne(query)
        account["id"] = userId[0]

        query = f"""
            SELECT SUM(transferamount) FROM transactions WHERE user_id_to={account["id"]};
        """

        transactionsTo = this_db.read(query)
        add = transactionsTo[0][0]
        
        query = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from={account["id"]};
        """

        transactionsFrom = this_db.read(query)
        sub = transactionsFrom[0][0]

        if add != None and sub != None:
            account["balance"] = round(add - sub, 2)
        elif add == None and sub == None:
            account["balance"] = 0
        elif add != None and sub == None:
            account["balance"] = round(add, 2)
        elif add == None and sub != None:
            account["balance"] = round(sub, 2)


        return render_template("transfer.html", account=account)
    

    else:
        try:
            username = session['username']
        except KeyError:
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
        SELECT id FROM users WHERE name='{username}'
        """

        q = this_db.readOne(query)
        fromid = q[0]

        balance = 0

        q = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_to='{fromid}'
        """
        h = this_db.read(q)
        add = h[0][0]

        q = f"""
        SELECT SUM(transferamount) FROM transactions WHERE user_id_from='{fromid}'
        """
        h = this_db.read(q)
        sub = h[0][0]

        if add != None and sub != None:
            balance = round(add - sub, 2)
        elif add == None and sub == None:
            flash("You can't transfer more than you have!")
            return redirect(url_for("transfer"))
        elif add != None and sub == None:
            balance = round(add, 2)
        elif add == None and sub != None:
            balance = round(sub, 2)

        # get balance

        if balance - float(request.form["amount"]) < 0:
            flash("You can't transfer more than you have!")
            return redirect(url_for("transfer"))

        query = f"""
        SELECT id FROM users WHERE name='{request.form["name"]}'
        """

        q = this_db.readOne(query)
        print(toid)
        try:
            toid = q[0]
        except TypeError:
            flash("Enter valid username!")
            return redirect(url_for("transfer"))

        if fromid == toid:
            flash("You can't transfer to yourself!")
            return redirect(url_for("transfer"))

        query = f"""
        INSERT INTO transactions (transferamount, user_id_to, user_id_from) VALUES ({request.form["amount"]}, {toid}, {fromid}); 
        """

        this_db.execute(query)

        this_db.close()

        flash("Transfer complete!")
        return redirect(url_for("transfer"))


@app.route("/adminpanel", methods=["GET", "POST"])
def adminpanel():
    if request.method == "GET":
        return render_template("adminpanel.html")
    
    if request.form["name"] == "" or request.form["amount"] == "":
        flash("You need to fill in the form completely!")
        return redirect(url_for("transfer"))

    this_db = db()
    this_db.connect("data.sql")

    query = f"""
    SELECT id FROM users WHERE name='{request.form["name"]}'
    """

    idq = this_db.readOne(query)

    try:
        toid = idq[0]
    except TypeError:
        flash("Invalid user!")
        return redirect(url_for("adminpanel"))
    
    query = f"""
    INSERT INTO transactions (transferamount, user_id_to) VALUES ({request.form["amount"]}, {toid});
    """

    this_db.execute(query)

    print(toid)

    flash("Transfer complete!")
    return redirect(url_for("adminpanel"))




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        try:
            test = session['username'] # try to cause a KeyError lmao
            test = None
            return redirect(url_for("index"))
        except KeyError:
            return render_template("login.html")
        
    elif request.method == "POST":
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