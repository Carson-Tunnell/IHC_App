import SQLHelper as SQ
import datetime as dt
import pprint as pp
# Determines how long it would take the crew to go home
# uses the homebase as the destination and current 
# assignment as the origin location
# returns time needed to get home in hours
def calcTimeNeeded(crewID,reqID,cursor):
    # Find crew distance to homebase based on date given
    dist = SQ.getDistance(crewID,reqID,cursor)
    print("Dist: ", dist)
    if (dist != None):
        dist = dist[2]
    else:
        return dt.timedelta(hours=5000.0)
    # divide distance by 40 mph
    hours = dist/40.0
    # if over 12 hours must add 12 hours to overall time.   
    overtime = int (hours / 12.0)
    hours += (overtime * 12) 
    # Adding the two days of R&R that need to be taken off to recover
    hours += 48
    result = dt.timedelta(hours=hours)
    return result


 # mob ETA - Demob ETD
def findGap(crewID,date,cursor):
    # searches the SQL for a given crew and date
    # Get all requests older than current date
    # [11] is MOB ETA
    # [13] is DEMOB ETD
    rows = SQ.getDatesOld(crewID,date,cursor)  
    print(len(rows))
    reqIDGap = -1
    # Checks if crew is assigned after most recent assignment 
    if (not checkFirstRow(crewID,rows[0],date,cursor)):
        for i in range(len(rows) - 1):
            # determines how long it would take to go to homebase on current assignmnet 
            timeHome = calcTimeNeeded(crewID,rows[i][0],cursor)
            # determines how long the gap between assignmnets actually is
            timeBetween = gapCalc(rows[i][11],rows[i + 1][13])
            print(timeHome)
            print(timeBetween)
            if(timeHome != None and timeBetween != None):  
                # diff is the difference between the time it would take to get home and the time they have
                # if it is positive then the crew is at their homebase
                diff = (timeBetween - timeHome)
                delta = diff.total_seconds()
                print("Delta: ", delta)
                # Positive means that the crew CAN return home for R and R
                if delta >= 0:
                    print("POSITIVE: ", diff)
                    reqIDGap = i
            if(reqIDGap != -1):
                break
        if(reqIDGap != -1):
            getPrevReqDays(rows,i,crewID,date,cursor)

    else:
        return 14
        
# Takes the current found request and then determines how many days are left        
def getPrevReqDays(rows,i,crewID,date,cursor):
    reqIDcurr = rows[i][0]
    fourteenDays = dt.timedelta(days=14)
    timeToSite = calcTimeNeeded(crewID,reqIDcurr,cursor)
    # Determines how many days the crew has from the start ETA of the next job
    daysLeft = fourteenDays - timeToSite
    # Check about 2pm stuff here

    givenDate =  dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    daysFromETA = givenDate - rows[i][11]
    print(givenDate)
    print(daysLeft)
    print(daysFromETA)


    print()
# Determines if the date provided for the CrewID is during an assignment
def findRequest(crewID,date,cursor):
    request = SQ.findRequestDate(date,crewID,cursor)
    if(request != None or request != "null"):
        return request
    else:
        return None


def checkPositive(rows,index):
    print()

# Checks if the crew is available from the last assignment
# if true this means the crew is currently unassignmed or has 14 days available to work
# if false then we need to calculate how many days left on assigment they have
def checkFirstRow(crewID,row,date,cursor):
    givenDate =  dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    timeHome = calcTimeNeeded(crewID,row[0],cursor)
    timeBetween = gapCalc(row[13],givenDate)

    if(timeHome != None and timeBetween != None):  
        # diff is the difference between the time it would 
        diff = (timeHome - timeBetween )
        delta = diff.total_seconds()
        print(delta)
        # Positive means that the crew CAN return home for R and R
        if delta > 0:
            print("GivenDate: ", givenDate)
            print("FoundDate: " , row[13])
            print("TRUE")
            return True
        #Negative means that the crew CANNOT return home in the given time
        if(delta < 0):
            print("False")
            return False
    return False

# Returns the difference between two times
def gapCalc(time1,time2):
    if(time1 == None or time2 == None):
        return None    
    #zero = datetime.datetime(0000,00,00,00,000,000)
    elif (time1 - time2 == time1 or time2 - time1 == time2):
        return None
    return abs(time1 - time2) 

# returns all the requests from the previous 28 day cycle 
# uses these request to determine time for the crew to go home
# returns list of all historical data
def get28Days(crewID, date):
    print()

# Checks in the current assignment gap was long enough to go home
# if it was returns true otherwise false
def checkGap(gapTime,assign1,assign2):
    return False

if __name__ == '__main__':

    conn = SQ.connectDB("root","Code","localhost","iht_test")
    cursor = conn.cursor(buffered=True)
    print("Days Left: ", findGap(1330,"2018-05-16 16:35:00",cursor))

    #timeActual = calcTimeNeeded(16,8087625,cursor)

    print()