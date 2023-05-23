def sqlsafe(sql):
    ret = sql.replace("'", "")
    return ret

def sqlsafeint(sql):
    int(sql) # tries to throw error
    return sql

def sqlsafefloat(sql):
    float(sql)
    return sql