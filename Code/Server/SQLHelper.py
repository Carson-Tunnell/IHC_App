import time
import imaplib, email, os
import xlrd
import csv
import pprint
from mysql.connector import (connection)
import datetime
debug = False

# Connects to a database to run SQL queries and store data on
def connectDB(user,password,host,database,port=3307):
    conn = connection.MySQLConnection(user=user, password=password,host=host,database=database,port=port)
    if (conn.is_connected()):
        print('Connected to MySQL database')
    return conn

# Used when dealing with Request Data
# Updates History table and Requst table
def update_all(file,cursor,date=None):
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

# Updates all crew data into the Crews table
def update_crews(file,cursor,date=None):
    header = file.readline().split(',')
    dupe_list = find_duplicate_cols(header)
    for line in file.readlines():
        line = del_duplicate_cols(line,dupe_list)
        crew_check_match(line,cursor,header)

# Checks to make sure we dont have a duplicate entry in the Databse
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

# Checks for duplicates before adding to the a table
# Prevents duplicated data
# TODO Needs to ignore the date column from email time when checking for duplicates
def check_before_add(splat,cursor,header):
    query = "SELECT * From requests WHERE "
    for i in range(len(header)):
        if(dateCheck(header[i])):
            splat[i] = fixDate(splat[i])
        if(IDcheck((header[i]))):
            splat[i] = fixID(splat[i])
        splat[i] = checkValid(splat[i])
        #print("After fix:{",splat[i] +"}")
        query += "`%s` = %s AND " %(header[i].rstrip().replace("\"",""),splat[i].rstrip())
    query = query[:-5]
    query += ";"
    #print("Check add: ", query)
    cursor.execute(query)    
    result = cursor.fetchone()

    if (result != None):
        return True
    else:
        return False


# Checks for duplicates before adding to the a table
# Prevents duplicated data
def check_before_add_Crew(splat,cursor,header):
    query = "SELECT * From crew_status WHERE "
    for i in range(len(header)):
        if(dateCheck(header[i])):
            splat[i] = fixDate(splat[i])
        if(IDcheck((header[i]))):
            splat[i] = fixID(splat[i])
        splat[i] = checkValid(splat[i])
        #print("After fix:{",splat[i] +"}")
        query += "`%s` = %s AND " %(header[i].rstrip().replace("\"",""),splat[i].rstrip())
    query = query[:-5]
    query += ";"
    #print("Check add: ", query)
    cursor.execute(query)    
    result = cursor.fetchone()

    if (result != None):
        return True
    else:
        return False


def insertReqHistory(splat,cursor,header):
    if (not check_before_add(splat,cursor,header)):
        history_query = "INSERT INTO history Values ("
        count = 0
        for i in splat:
            if(dateCheck(header[count])):
                i = fixDate(i)
            if(IDcheck((header[count]))):
                i = fixID(i)
            i = checkValid(i)
            if ("\"" in str(i)):
                history_query += i.rstrip() + ", "
            else:
                history_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
            count += 1
        history_query = history_query[:-2] 
        history_query += ",\"0\");"
        #print("History: ", history_query)
        cursor.execute(history_query)

def insertCrewHistory(splat,cursor,header):
    if (not check_before_add_Crew(splat,cursor,header)):
        history_query = "INSERT INTO crewhistory Values ("
        count = 0
        for i in splat:
            if(dateCheck(header[count])):
                i = fixDate(i)
            if(IDcheck((header[count]))):
                i = fixID(i)
            i = checkValid(i)
            if ("\"" in str(i)):
                history_query += i.rstrip() + ", "
            else:
                history_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
            count += 1
        history_query = history_query[:-2] 
        history_query += ",\"0\");"
        #print("History: ", history_query)
        cursor.execute(history_query)


# If data is not in the database this creates a new entry for it
# used when we are not updating old entries
def add_unique(splat,cursor,header,date=None):
    #inserts into history table
    insertReqHistory(splat,cursor,header)

    requests_query = "INSERT INTO requests Values ("
    count = 0
    for i in splat:
        if(dateCheck(header[count])):
            i = fixDate(i)
        requests_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
        count += 1
    requests_query = requests_query[:-2] 
    requests_query += ");"
    #requests_query += ",\"0\");"
    #print(requests_query)
    cursor.execute(requests_query)

# Deletes duplicated columns in the intput CSV's
def del_duplicate_cols(row,dupe_list):
    row = row.rstrip().split(',')
    if len(dupe_list) > 0:
        for i in dupe_list:
            del row[i]
    return row

# Inserts data when a duplicate is found
def duplicate(splat,cursor,header):
    #Inserts into history table
    insertReqHistory(splat,cursor,header)
    
    #Updates Current entry in Requests
    query = "UPDATE requests SET "
    count = 0
    for i in range(len(header)):
        if(dateCheck(header[count])):
           splat[i] = fixDate(splat[i])
        if(IDcheck((header[count]))):
            splat[i] = fixID(splat[i])
        splat[i] = checkValid(splat[i])
        query += "`%s` = %s, " %(header[i].rstrip().replace("\"",""),splat[i].rstrip())
        count += 1

    query = query[:-2]
    query += " WHERE `Req ID` = %s " %splat[0].rstrip()
    #print(query)
    cursor.execute(query)
    


# Determines which columns in a CSV are duplicated
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

# Check if field is a date that needs to be converted 
    # Assign Date
    # Order Date GMT
    # Release Date
    # Demob ETD
    # Demob ETA
    # Mob ETA
    # Mob ETD
    # Need Date
    # Order Date
def dateCheck(headerVal):
    dateCols = ["Assign Date","Order Date GMT","Last Status Change Date",
                "Release Date","Demob ETD","Demob ETA",
                "Mob ETA", "Mob ETD","Need Date","Order Date"]
    if(headerVal[1:-1] in dateCols):
        return True
    else:
        return False

def IDcheck(headerVal):
    #print(headerVal)
    IDCols = ["Res ID", "Req ID","Inc ID"]
    if(headerVal[1:-1] in IDCols):
        return True
    else:
        return False

def checkValid(value):
    value = str(value).strip()
    #print("Value: {",value + "}")
    if(value == "" or value == "\""):
        return "\"\""
    elif("\"" in value[0] and "\""  in value[:-1]):
        return value
    else:
        return "\"" + value + "\""

def fixID(errID):
    #print("ErrID: ", errID)
    if("." in str(errID)):
        return errID[:-3] + "\""
    return errID   

# Converts the Excel date format into one that SQL can use
def fixDate(errDate):
    #print("Got: '", errDate ,"'")
    #Checks if date has already been corrected
    if("-" in errDate and ":" in errDate or "NULL" in errDate):
        return errDate.strip()

    if( r"/" in errDate):
        return errDate.strip()
    if(len(errDate) > 5 ):
        newDate = xlrd.xldate_as_tuple(float(str(errDate[0:]).replace("\"","")), 0)
        #print("New Date: ", newDate)
        strDate = str(newDate[0]) + "-" + str(newDate[1]) + "-" + str(newDate[3]) + " " + str(newDate[3]) + ":" + str(newDate[4]) + ":" + str(newDate[5])
        #print(datetime.datetime(newDate))
        ## Keep all precision from Excel Document
        ## Check Time zones for data
        #print("Date Str: ", strDate)
        return strDate
    else:
        return "0000-00-00 00:000:000"
#Gregorian (year, month, day, hour, minute, nearest_second). 
# Updates a crew row
def update_crew_line(splat,cursor,header): 
    insertCrewHistory(splat,cursor,header)
    query = "UPDATE Crew_Status SET "
    for i in range(len(header)):
        if(dateCheck(header[i])):
            splat[i] = fixDate(splat[i])   
        if(IDcheck((header[i]))):
            splat[i] = fixID(splat[i])
        splat[i] = checkValid(splat[i])      
        query += "`%s` = \"%s\", " %(header[i].rstrip().strip("\""), splat[i].rstrip().strip("\"").replace("\"",""))
    query = query[:-2]
    query += " WHERE `Res ID` = %s " %splat[11].rstrip()
    #print(query)
    cursor.execute(query)

# Inserts a new crew value into the database
def insert_new_crew(splat,cursor,header):
        insertCrewHistory(splat,cursor,header)
        crew_query = "INSERT INTO Crew_Status Values ("
        count = 0
        for i in splat:
            if(dateCheck(header[count])):
                i = fixDate(i)
            if(IDcheck((header[count]))):
                i = fixID(i)
            i = checkValid(i)
            crew_query += "\"" + i.rstrip().strip("\"") + "\"" + ", "
            count += 1
            #print(i.rstrip().strip("\""))
        crew_query = crew_query[:-2] 
        crew_query += ");"
        cursor.execute(crew_query)

#Returns true if the values are the same
#Returns false if the the values are different
def compare_crew(row,result,cursor,header):
    if (result == None):
        insert_new_crew(row,cursor,header)
        return True
    for i in range(len(row)):
        #print(i ,": ", row[i])
        if row[i] != str(result[i]):
            return False
    return True

# checks if the crew is already in the table
# [11] is the crew name
def crew_check_match(splat,cursor,header):
    if(splat[11] != None):
        cursor.execute("SELECT * FROM Crew_Status WHERE `Res ID` = %s" % splat[11])
        row = cursor.fetchone()
        if(not compare_crew(splat,row,cursor,header)):
            update_crew_line(splat,cursor,header)

def getDatesOld(crewID,date,cursor):
    query = "SELECT * FROM iht_test.history WHERE \
             `Res ID` like '" + str(crewID) + "' AND \
             `Order Date` <= '" + date + "'ORDER BY `Demob ETA` DESC;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getDatesNew(crewID,date,cursor):
    query = "SELECT * FROM iht_test.history WHERE \
             `Res ID` like '" + str(crewID) + "' AND \
             `Order Date` >= '" + date + "'ORDER BY `Demob ETA` DESC;"
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def getDistance(crewID,reqID,cursor):
    query = "SELECT * FROM iht_test.distancelookup WHERE \
             `ResID` like '" + str(crewID) + "' AND \
             `DestIncID` like '" + str(reqID) + "';"
    cursor.execute(query)
    result = cursor.fetchone()
    return result

# Find the request for a crewID that is during the date specified
# returns none if the crew is not assigned
def findRequestDate(date,crewID,cursor):
    query = "SELECT * FROM iht_test.history WHERE \
            `Res ID` like '" + crewID + "' and `Mob ETA` <= '" + date + \
            "' and `Demob ETD` >= '" + date +  "';"
    cursor.execute(query)
    result = cursor.fetchone()
    return result

