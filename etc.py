from datetime import datetime
from datetime import timedelta
from db import db

def getDate(date):
    return datetime.strptime(date, '%Y-%m-%d').date()

def updateWeekly(): # TODO set timestamp to midnight of correct friday
    database = db()
    database.connect("data.sql")

    now = datetime.now().date()
    weekday = now.weekday() # friday is 4

    query = f"""
    SELECT date FROM updates ORDER BY id DESC LIMIT 1;
    """

    mostrecent = getDate(database.readOne(query)[0])

    diff = (now - mostrecent).days

    weeks = int(diff / 7)

    if mostrecent.weekday() != 4: # check if last update was a friday
        return "oh shit" # TODO oh shit
    if mostrecent == now or diff < 7:
        return 0

    print(f"full weeks since last update: {weeks}")

    query = f"""
    SELECT id FROM users ORDER BY id;
    """
    users = database.read(query)

    

    for user in users:
        userid = user[0]

        query = f"""
        SELECT birthdate FROM users WHERE id={userid};
        """
        read = database.readOne(query)[0]
        if read == None:
            continue

        dob = getDate(read)
        #print(f"dob for user {userid}: {dob}")
        weekly = int(((now - dob).days) / 365.2425) * 0.75 # might be bad
        #print(f"weekly of user {userid}: {weekly}")

        date = mostrecent
        while True: # maybe todo? switch while and for loop positions (clean up transaction ids)
            date += timedelta(days=7)
            print(date)
            if date > now:
                break
            query = f"""
            INSERT INTO
                transactions(transferamount, user_id_to, timestamp)
            VALUES
                ({weekly}, {userid}, '{datetime.combine(date, datetime.min.time())}');
            """
            database.execute(query)

    stage = mostrecent
    date = mostrecent
    while True:
        stage += timedelta(days=7)
        if stage > now:
            break
        date = stage

    print(f"updating last update to {date}")

    query = f"""
    INSERT INTO
        updates(date)
    VALUES
        ('{date}');
    """

    database.execute(query)
    
    