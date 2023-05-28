def init_db(database):

    create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        birthdate DATE,
        name TEXT NOT NULL UNIQUE,
        administrator BOOLEAN,
        hash TEXT
    );"""

    database.execute(create_users)

    create_transactions = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        transferamount FLOAT NOT NULL,
        user_id_to INTEGER NOT NULL, 
        user_id_from INTEGER,
        timestamp DATETIME NOT NULL DEFAULT(current_timestamp),
        FOREIGN KEY (user_id_to) REFERENCES users (id),
        FOREIGN KEY (user_id_from) REFERENCES users (id)
        
    );
    """

    database.execute(create_transactions)

    create_weeklyupdate = """
    CREATE TABLE IF NOT EXISTS updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL
    );
    """

    database.execute(create_weeklyupdate)

    # TODO ADD BIRTHDATE TO TEST DATA
    test = """ 
    INSERT INTO 
        users (name, administrator, hash, birthdate)
    VALUES
        ('noah', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d', '2007-09-26'),
        ('cole', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d', '2011-09-14'),
        ('dylan', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d', '2011-09-14'),
        ('nick', true, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d', NULL);
    """

    test2 = """ 
    INSERT INTO 
        transactions (transferamount, user_id_to, user_id_from)
    VALUES
        (10, 1, 4),
        (10, 1, 4),
        (3.7, 1, 4),
        (20.04, 1, 4);
    """

    test3 = """
    INSERT INTO
        updates(date)
    VALUES
        ('2023-5-21');
    """

    #database.execute(test)
    #database.execute(test2)
    #database.execute(test3)