from datetime import datetime

def getDate(date):
    return datetime.strptime(date, '%Y-%m-%d').date()