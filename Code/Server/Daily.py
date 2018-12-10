import schedule
import time
import imaplib, email, os
import xlrd
import csv

#iht8303362630@gmail.com
#830336263

def morning_run():
    print("8am")
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    download = mainPath + r"\IHT Project\Data\Server\Daily Test\8am"
    address  = "username@gmail.com"
    password = "password"
    con = connect(address,password)
    emailNumbers = get_unread(con)
    if (emailNumbers != None):
        for i in emailNumbers:
            result, data = con.fetch(i,'(RFC822)')
            raw = email.message_from_bytes(data[0][1])
            get_attachments(download,raw)
    files8am = [download + r"\Report View of CREW REQUEST AUTOMATED QUERY - ONCE DAILY 0800.xlsx"
               ,download + r"\Report View of CREW REQUEST AUTOMATED QUERY - Released in prior 48 hours - ONCE DAILY AT 0800.xlsx"
               ,download + r"\Report View of CREW STATUS TABLE - ONCE DAILY 0800.xlsx"]
    csv_from_excel(files8am)

def evening_run():
    print("5pm")
    address  = "username@gmail.com"
    password = "password"
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    download = mainPath + r"\IHT Project\Data\Server\Daily Test\5pm"

    con = connect(address,password)
    emailNumbers = get_unread(con)
    if (emailNumbers != None):
        for i in emailNumbers:
            result, data = con.fetch(i,'(RFC822)')
            raw = email.message_from_bytes(data[0][1])
            get_attachments(download,raw)
    files5pm = [download + r"\Report View of CREW REQUEST AUTOMATED QUERY - ONCE DAILY 1700.xlsx"
               ,download + r"\Report View of CREW STATUS TABLE - ONCE DAILY 1700.xlsx"]
    csv_from_excel(files5pm)

def connect(usr,pwd):
    con = imaplib.IMAP4_SSL("imap.gmail.com")
    con.login(usr,pwd)
    con.select("INBOX")
    return con

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

def get_attachments(download,msg):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            fileName = fileName.replace('\n','')
            fileName = fileName.replace('\r ',' ')
            print(fileName)
            filePath = os.path.join(download, fileName)
            try:
                with open(filePath,'wb') as f:
                    f.write(part.get_payload(decode=True))
            except FileNotFoundError:
                print("File Not Found: Waiting for next cycle to check again")
                continue

def csv_from_excel(filenames):
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
            wr.writerow(clean_csv_line(sh.row_values(rownum)))
        converted.close()

def clean_csv_line(lineList):
    for i in range(len(lineList)):
        lineList[i] = str(lineList[i]).rstrip()
        lineList[i] = str(lineList[i]).replace(',','__')
        lineList[i] = str(lineList[i]).replace('"','')
    return lineList

def test():
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    download = mainPath  + r"\IHT Project\Data\Server\Daily Test\8am"
    files8am = [download + r"\Report View of CREW REQUEST AUTOMATED QUERY - ONCE DAILY 0800.xlsx"
               ,download + r"\Report View of CREW REQUEST AUTOMATED QUERY - Released in prior 48 hours - ONCE DAILY AT 0800.xlsx"
               ,download + r"\Report View of CREW STATUS TABLE - ONCE DAILY 0800.xlsx"]
    csv_from_excel(files8am)

if __name__ == '__main__':

    test()
#    schedule.every().day.at("8:10").do(morning_run)
#    schedule.every().day.at("17:10").do(evening_run)
 #   while True:
  #      schedule.run_pending()
   #     time.sleep(1)
    
    #Must run at 8am and pulls ALL unread emails
    #morning_run()
    #Must run at 5pm and pulls ALL unread emails
    #evening_run()

    #https://stackoverflow.com/questions/20105118/convert-xlsx-to-csv-correctly-using-python