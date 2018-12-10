import time
import imaplib, email, os
import xlrd
import csv
import pprint
from mysql.connector import (connection)
import datetime
import SQLHelper as SQ
debug = False

#######################################################################################
#################################  Email Code #########################################
#######################################################################################

# Connects to the Users GMAIL 
# Takes username and password
def connectEmail(usr,pwd):
    con = imaplib.IMAP4_SSL("imap.gmail.com")
    con.login(usr,pwd)
    con.select("INBOX")
    return con
# Returns a list of all unread emails in the inbox
# Needs a connection to check
def get_unread(con):
    unread = con.search(None,'UnSeen')
    if len(unread[1][0]) == 0:
        return None
    data = str(unread[1][0])
    data = data[2:-1]
    splat = data.split(' ') 
    for i in splat:
        i = chr(int(i))
    return splat

# Downloads the attatchments from an email object
# Converts the excel attatchemnt to a CSV
# Also adds the date column to the CSV
def get_attachments(download,msg,date=None):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            fileName = fileName.replace('\n','')
            fileName = fileName.replace('\r ',' ')
            filePath = os.path.join(download, fileName)
            try:
                with open(filePath,'wb') as f:
                    f.write(part.get_payload(decode=True))
            except FileNotFoundError:
                print("File Not Found: Waiting for next cycle to check again")
                continue
            if(date != None):
                csv_from_excel([filePath],date=date)
            else:
                csv_from_excel([filePath])

# Takes a list of filenames
# Converts the files from Excel to CSV
# Cleans up rows and replaces commas with '__'
def csv_from_excel(filenames,date=None):
    for i in filenames:
        wb = xlrd.open_workbook(i)
        sh = wb.sheet_by_name('page')
        try:
            converted = open(i[:-4] + "csv", 'w',newline='')
        except FileNotFoundError:
            print("File Not Found: Waiting for next cycle to check again")
            continue
        wr = csv.writer(converted, quoting=csv.QUOTE_ALL)
        for rownum in range(sh.nrows):
            if(rownum == 0):
                 wr.writerow(clean_csv_line(sh.row_values(rownum),date="Date"))
            else:
                wr.writerow(clean_csv_line(sh.row_values(rownum),date=date))
        converted.close()

# Cleans the rows by removing conflicting characters
def clean_csv_line(lineList,date=None):
    for i in range(len(lineList)):
        lineList[i] = str(lineList[i]).rstrip()
        lineList[i] = str(lineList[i]).replace(',','__')
        lineList[i] = str(lineList[i]).replace('"','')
    if(date != None):
        lineList.append(date)
    return lineList

# Start function is what main used to be
# Created so that we can call all the code from one main driver class
# allows us to only have to schedule one program to run daily
def start():
    # This should be removed if ever committed to an online place or shared
    address  = "username@gmail.com"
    password = "password"
     
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    download = mainPath + r"\IHT Project\Data\Server\Daily Test\Full"

    con = connectEmail(address,password)
    emailNumbers = get_unread(con)
    print("Unread: ", emailNumbers)
    count = 1
    conn = SQ.connectDB("root","Code","localhost","iht_test")
    cursor = conn.cursor(buffered=True)
    # Checks if we have unread emails
    if (emailNumbers != None):
        # Iterates through all the unread emails
        for i in emailNumbers:
            print("Running: " ,str(count) + " / " , len(emailNumbers))
            #### Email Download and Process ####
            result, data = con.fetch(i,'(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            temp = data[0][1].splitlines()
            date = str(temp[2][12:] )
            date = date[3:-1]
            get_attachments(download,msg,date=date)

            # Gets the filename of the downloaded attatchemnts
            fileName = "blank"
            for part in msg.walk():
                if(fileName == "blank" or fileName == None):
                    fileName = part.get_filename()

            fileName = fileName[:-4] + "csv"
            fileName = fileName.replace('\n','')
            fileName = fileName.replace('\r ',' ')
            # Determines which file we are dealing with and processes accordingly
            if("Report View of CREW STATUS TABLE - ONCE DAILY" in fileName):
                #print("Update Crews")
                crewsFile = open(download + "\\" + fileName)
                SQ.update_crews(crewsFile,cursor)
                conn.commit()  

            elif ("Report View of CREW REQUEST AUTOMATED QUERY - Released in prior 48 hours" in fileName):
                #print("Update All")
                requestFile = open(download + "\\" + fileName)    
                SQ.update_all(requestFile,cursor)
                conn.commit()  

            elif ("Report View of CREW REQUEST AUTOMATED QUERY - ONCE DAILY" in fileName):
                #print("Update All")
                requestFile = open(download + "\\" + fileName)    
                SQ.update_all(requestFile,cursor)
                conn.commit()  
            count += 1

#FLOW
#Determine which email we have
#Download Email
#Get Date of Email
#Add date columns to CSV files

#Use SQL to input into database
    #Once Daily Request = update_all
    #Once Daily Crew = update_crews
#Download Next file
       
if __name__ == '__main__':
    start()