from mysql.connector import (connection)


debug = True

def update_all(file,cursor):
    header = file.readline().split(',')

    for line in file.readlines():
        if (check_duplicate(line,cursor,header)):
            print("Duplicate")
            duplicate(line,cursor,header)
        else:
            print("Unique")

def check_duplicate(row,cursor,header):
    
    splat = row.split(',')
    if(splat[0] != None):
        print("Looking up: ", splat[0])
        cursor.execute("SELECT * FROM requests WHERE `Req ID` = %s" % splat[0])
        row = cursor.fetchone()

        if (row != "None"):
            if (debug): print("True")
            return True
        else:
            if (debug): print("False")
            return False

def duplicate(row,cursor,header):
    splat = row.split(',')
    history_query = "INSERT INTO history Values ("
    for i in splat:
        history_query += "\"" + i.rstrip() + "\"" + ", "
    history_query = history_query[:-2] 
    history_query += ",\"0\");"
    cursor.execute(history_query)
    #printDB(cursor)
    
    #Updates Current entry in Requests
    query = "UPDATE requests SET "
    for i in range(len(header)):
        query += "`%s` = \"%s\", " %(header[i].rstrip(),splat[i].rstrip())

    query = query[:-2]
    query += " WHERE `Req ID` = \"%s\" " %splat[0].rstrip()
    cursor.execute(query)
    #print(query)

def printDB(cursor):
    print("SELECT * FROM iht_test.history;")
    cursor.execute("SELECT * FROM iht_test.history;")
    print(cursor.fetchone())

def connect(user,password,host,database,port=3307):
    conn = connection.MySQLConnection(user=user, password=password,host=host,database=database,port=port)
    if (conn.is_connected()):
        print('Connected to MySQL database')
    return conn

if __name__ == '__main__':

    #cnx = connection.MySQLConnection(user='cwis122', password='JY7}Jn5BzBnG',host='respond.colostate.edu',database='cwiss122_Test')
    update_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Server\Requests\Test\Update.csv"
    conn = connect("root","Code","localhost","iht_test")
    
    csv = open(update_path)
    cursor = conn.cursor()

    update_all(csv,cursor)


    row = cursor.fetchone()
 
    while row is not None:
        print(row)
        row = cursor.fetchone()

    '''  cursor.execute("SELECT * FROM history")
    row = cursor.fetchone()
 
    while row is not None:
        print(row)
        row = cursor.fetchone()

    #cursor.execute("DELETE FROM history WHERE 'Req ID' = 'Req ID' ;")
    # row = cursor.fetchone()
    print(row)'''

    conn.commit()
    cursor.close()
    conn.close()
    
    print()

    


    #"DELETE FROM table_name WHERE condition;"


   