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

    # timestamp TIMESTAMP NOT NULL, could be added but not that terribly important
    create_transactions = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        transferamount FLOAT NOT NULL,
        user_id_to INTEGER NOT NULL, 
        user_id_from INTEGER,
        FOREIGN KEY (user_id_to) REFERENCES users (id),
        FOREIGN KEY (user_id_from) REFERENCES users (id)
    );
    """

    database.execute(create_transactions)

    # TODO ADD BIRTHDATE TO TEST DATA
    test = """ 
    INSERT INTO 
        users (name, administrator, hash)
    VALUES
        ('noah', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d'),
        ('cole', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d'),
        ('dylan', false, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d'),
        ('nick', true, 'd4f6d068b4e8c4e924ce9b28585a6009672e56d61215e7d9251b5d36283edd5d');
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

    #database.execute(test)
    #database.execute(test2)