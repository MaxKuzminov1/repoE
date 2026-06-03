import MySQLdb as mdb

def select(query, params=()):
    con = mdb.connect('localhost', 'root', 'root', 'shoes_shop2')
    cur = con.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    con.close()
    return data

def execute(query, params=()):
    con = mdb.connect('localhost', 'root', 'root', 'shoes_shop2')
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()
    con.close()