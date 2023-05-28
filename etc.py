from datetime import datetime
from datetime import timedelta
from db import db

def getDate(date):
    return datetime.strptime(date, '%Y-%m-%d').date()

def updateWeekly():
    database = db()
    database.connect("data.sql")

    now = datetime.now().date()
    weekday = now.weekday() # friday is 4

    query = f"""
    SELECT date FROM updates ORDER BY id DESC LIMIT 1;
    """

    mostrecent = getDate(database.readOne(query)[0])


    if mostrecent < now and weekday == 4:

        diff = (now - mostrecent).days
        weeks = int(diff / 7)

        print(f"Diff: {diff}")

        query = f"""
        SELECT id FROM users ORDER BY id;
        """

        users = database.read(query)

        for user in users:
            userid = user[0]
            
            query = f"""
            SELECT birthdate FROM users WHERE id={userid}
            """
            read = database.readOne(query)[0]
            if read == None:
                continue

            dob = getDate(read)

            print(f"dob for user {userid}: {dob}")

            weekly = int(((now - dob).days) / 365.2425) * 0.75 # might be bad

            print(f"weekly of user {userid}: {weekly}")

            # TODO set timestamp to midnight of correct friday
            query = f"""
            INSERT INTO 
                transactions(transferamount, user_id_to)
            VALUES
                ({weekly * weeks}, {userid});
            """

            database.execute(query)

        query = f"""
        INSERT INTO
            updates(date)
        VALUES
            ('{now}');
        """

        database.execute(query)
    
    