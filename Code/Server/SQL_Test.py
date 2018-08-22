from mysql.connector import (connection)
#   cd '.\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Code\Server\'

debug = False

def update_all(file,cursor):
    header = file.readline().split(',')
    dupe_list = find_duplicate_cols(header)
    for line in file.readlines():
        line = del_duplicate_cols(line,dupe_list)
        if (check_duplicate(line,cursor,header)):
            if(debug):print("Duplicate")
            duplicate(line,cursor,header)
        else:
            if(debug):print("Unique")
            check_before_add(line,cursor,header)
            add_unique(line,cursor,header)

def update_crews(file,cursor):
    header = file.readline().split(',')
    dupe_list = find_duplicate_cols(header)
    for line in file.readlines():
        line = del_duplicate_cols(line,dupe_list)
        crew_check_match(line,cursor,header)

def find_duplicate_cols(header):
    dupe_list = []
    for i in range(len(header)):
        for j in range(i + 1,len(header)):
            if header[i] == header[j]:
                if(debug):print(header[i] ," : is a duplicate")
                dupe_list.append(i)

    if len(dupe_list) > 0:
        for i in dupe_list:
            del header[i]

    return dupe_list

def del_duplicate_cols(row,dupe_list):
    row = row.rstrip().split(',')
    if len(dupe_list) > 0:
        for i in dupe_list:
            del row[i]
    return row

def crew_check_match(splat,cursor,header):
    if(splat[11] != None):
        cursor.execute("SELECT * FROM Crew_Status WHERE `Res ID` = %s" % splat[11])
        row = cursor.fetchone()
        if(not compare_crew(splat,row,cursor)):
            update_crew_line(splat,cursor,header)
            

def update_crew_line(splat,cursor,header): 
    query = "UPDATE Crew_Status SET "
    for i in range(len(header)):
        query += "`%s` = \"%s\", " %(header[i].rstrip().strip("\""),splat[i].rstrip().strip("\""))
    query = query[:-2]
    query += " WHERE `Res ID` = \"%s\" " %splat[11].rstrip()
    cursor.execute(query)

def insert_new_crew(splat,cursor):
        crew_query = "INSERT INTO Crew_Status Values ("
        for i in splat:
            crew_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
            #print(i.rstrip().strip("\""))
        crew_query = crew_query[:-2] 
        crew_query += ");"
        cursor.execute(crew_query)
#Returns true if the values are the same
#Returns false if the the values are different
def compare_crew(row,result,cursor):
    if (result == None):
        insert_new_crew(row,cursor)
        return True
    for i in range(len(row)):
        #print(i ,": ", row[i])
        if row[i] != str(result[i]):
            return False
    return True

def check_duplicate(splat,cursor,header):
     if(splat[0] != None):
        if(debug):print("Looking up: ", splat[0])
        cursor.execute("SELECT * FROM requests WHERE `Req ID` = %s" % splat[0])
        row = cursor.fetchone()
        if (row != None):
            if (debug): print("True")
            return True
        else:
            if (debug): print("False")
            return False

def check_before_add(splat,cursor,header):

    query = "SELECT * From requests WHERE "
    for i in range(len(header)):
        query += "`%s` = \"%s\" AND " %(header[i].rstrip(),splat[i].rstrip())
    query = query[:-5]
    query += ";"
    cursor.execute(query)

    result = cursor.fetchone()

    if (result != None):
        return True
    else:
        return False

def add_unique(splat,cursor,header):
    print(len(splat))

    if (not check_before_add(splat,cursor,header)):
        history_query = "INSERT INTO history Values ("
        for i in splat:
            history_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
            print(i.rstrip().strip("\""))
        history_query = history_query[:-2] 
        history_query += ",\"0\");"
        cursor.execute(history_query)

    requests_query = "INSERT INTO requests Values ("
    for i in splat:
        requests_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
    requests_query = requests_query[:-2] 
    requests_query += ");"
    #requests_query += ",\"0\");"
    print(requests_query)
    cursor.execute(requests_query)


def duplicate(splat,cursor,header):
    if (not check_before_add(splat,cursor,header)):
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
    update_path = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Server\Requests\Test\Dupe_Test.csv"
    crew_path   = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Server\Crew_Status\Test\Full.csv" 
    conn = connect("root","Code","localhost","iht_test")
    
    csv = open(update_path)
    cursor = conn.cursor()
    
    update_all(csv,cursor)
    conn.commit()    

    row = cursor.fetchone()

    while row is not None:
        print(row)
        row = cursor.fetchone()

    
    #Update Crew Data
    crew_update = open(crew_path)    
    update_crews(crew_update,cursor)

    conn.commit()  
    print("Committed Changes to Database")  
    cursor.close()
    conn.close()
    print("Disconnected from Database")


   