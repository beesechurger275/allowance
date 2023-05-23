def sqlsafe(sql):
    ret = sql.replace("'", "")
    return ret