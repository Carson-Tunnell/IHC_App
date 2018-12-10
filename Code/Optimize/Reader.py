# This program goes through and processes input files for optimization
# used as a helper class for Optimize_Driver

#opens file from path given
#looks through pending requests and finds ones that are valid
#returns a list of valid requests
#returns reqID,Lat,Long of a given request
import pprint
from mysql.connector import (connection)
import Forecast
from shapely.geometry import Point

# Calls SQL to get all pending requests
def get_pending(cursor):
    valid_list = []
    query = "SELECT `Req ID`, `Lat Decimal`,`Long Decimal` \
         FROM iht_test.requests \
         WHERE `Req Status` like 'Pending'\
         and `Req Catalog Item Name` like 'Crew__ Type 1';"
    cursor.execute(query)
    data = cursor.fetchall()
    for i in data:
        valid_list.append([int(float(i[0])),float(i[1]),float(i[2])])
    return valid_list

# opens a connection to the database
def connect(user,password,host,database,port=3307):
    conn = connection.MySQLConnection(user=user, password=password,host=host,database=database,port=port,auth_plugin='mysql_native_password')
    if (conn.is_connected()):
        print('Connected to MySQL database')
    return conn

# Reads in the pending data from a CSV
# Legacy code before the switch to CSV
def read_pending(filename):
    file = open(filename)

    reqID_index = -1
    lat_index   = -1
    lng_index   = -1
    type_index  = -1
    valid_list = []
    header = file.readline().split(',')
    #find indexes for data
    for index in range(len(header)):
        if r"Lat Decimal" in header[index] :
            lat_index = index
        if r"Long Decimal" in header[index]:
            lng_index = index
        if r"Req ID" in header[index]:
            reqID_index = index
        if r"Req Catalog Item Name" in header[index]:
            type_index = index
    
    for line in file.readlines():
        line = line.replace("\"",'')
        splat = line.split(',')
        if splat[type_index] == "Crew__ Type 1":
            valid_list.append([int(float(splat[reqID_index])),float(splat[lat_index]),float(splat[lng_index])])
    return valid_list

# Gets the homebase table for crews
# returns it as a dictionary of crewID and the lat long
def get_homebase(cursor):
    valid_dict = {}
    query = "SELECT `Res ID`, `LatitudeFromAddress`,`LongitudeFromAddress` \
         FROM iht_test.homebase;"
    cursor.execute(query)
    data = cursor.fetchall()
    for i in data:
        valid_dict[int(float(i[0]))] = (float(i[1])),float(i[2])
    return valid_dict
    
# returns a dict of all homebase locations and their lat,lng
# key = resID  value = (lat,long)
# Creates a dict for fast lookup given a CrewID
def read_homebase(filename):
    file = open(filename)
    resID       = -1
    res_status  = -1
    valid_dict  = {}
    header = file.readline().split(',')
    #find indexes for data
    for index in range(len(header)):
        if r"Res ID" in header[index]:
            resID = index
        if r"LatitudeFromAddress" in header[index] :
            lat_index = index
        if r"LongitudeFromAddress" in header[index]:
            lng_index = index
      
    for line in file.readlines():
        splat = line.split(',')
        valid_dict[int(float(splat[resID]))] = (float(splat[lat_index]),float(splat[lng_index]))
    return valid_dict

# Returns list of all available crew resID's
# Crews returned are only ones that are "Crew_ Type 1" and "Available"
# **More criterias can be added here to filter out crews more correctly**

def get_crews(cursor):
    valid_list = []
    query = "SELECT  iht_test.crew_status.`Res ID`\
            FROM  iht_test.crew_status\
            INNER JOIN   iht_test.homebase ON iht_test.crew_status.`Res ID` = iht_test.homebase.`Res ID`\
            WHERE `Unavailable Flag` LIKE 'No' AND `Catalog Item Name` LIKE 'Crew__ Type 1';"
    cursor.execute(query)
    data = cursor.fetchall()
    for i in data:
        valid_list.append(int(float(i[0])))
    return valid_list

# Fuction to read in crews from file
# Legacy code from before SQL was implemented
def read_crews(filename):
    file = open(filename)

    resID      = -1
    res_status = -1
    crew_type  = -1
    valid_list = []
    header = file.readline().split(',')
    #find indexes for data
    for index in range(len(header)):
        if r"Res Status" in header[index] :
            res_status = index
        if r"Res ID" in header[index]:
            resID = index
        if r"Catalog Item Name" in header[index]:
            crew_type = index
      
    for line in file.readlines():
        line = line.replace("\"",'')
        line = line.replace("\n",'')
        splat = line.split(',')
        # Make sure Crew Type 1 has the correct amount of underscores ( _ ) for the input files
        if "Available" in splat[res_status] and  "Crew__ Type 1" in splat[crew_type]:
            valid_list.append(int(float(splat[resID])))
    return valid_list

# Writes the output to a file and adds the forecast data 
def write_file_forecast(filename,pending,homebase,crews):
    file = open(filename,'w+')
    #Creates the header the file needs for the distance program
    file.write("ResID,DestIncID,StartingPtLat,StartingPtLong,DestinationLat,DestinationLong,DistanceInMi,Forecast,TimeInSec,CrewToSend\n")
    # Runs the forecast code to get updated fire forecast data to input into file
    lookup = Forecast.run()
    for i in pending:
        for j in crews:
            homeLat  = 0.0
            homeLong = 0.0
            if j in homebase:
                homeLat  = str(homebase[j][0])
                homeLong = str(homebase[j][1])
                # TODO add circle data
                forecast = Forecast.point_lookup(lookup,Point(homebase[j][1],homebase[j][0]))
                # TODO add place to set weights as a global Day1ForcastWeight
                forecastAvg = (forecast[1] + forecast[2]/.5 + forecast[3]/.25)/3.0
                line_write = str(j) + "," + str(i[0]) + "," + str(homeLat) + "," + str(homeLong) + "," + str(i[1])  + "," + str(i[2]) + "," + "," + str(forecastAvg) + ", ," "\n"
            file.write(line_write)
    file.close()
    print("Written to: ", filename)


# old write method that doesnt include the forecast data
# Legacy code
def write_file(filename, pending,homebase,crews):
    file = open(filename,'w+')
    #Creates the header the file needs for the distance program
    file.write("ResID,DestIncID,StartingPtLat,StartingPtLong,DestinationLat,DestinationLong,DistanceInMi,Forecast,TimeInSec,CrewToSend\n")

    for i in pending:
        for j in crews:
            homeLat  = 0.0
            homeLong = 0.0
            if j in homebase:
                homeLat  = str(homebase[j][0])
                homeLong = str(homebase[j][1])

            line_write = str(j) + "," + str(i[0]) + "," + str(homeLat) + "," + str(homeLong) + "," + str(i[1])  + "," + str(i[2]) + "\n"
            file.write(line_write)
    file.close()
    print("Written to: ", filename)


# Start method to allow remote running from other Driver class
def start():
    print("Running Reader")

    # commented file paths can be used for legacy code
    mainPath = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018"
    #path =   r"\IHT Project\Data\Server\Daily Test\8am"
    #pending  = mainPath + path + r"\Report View of CREW REQUEST AUTOMATED QUERY - ONCE DAILY 0800.csv"
    #homebase =  mainPath + r"\IHT Project\Data\Optimize Data\HomeBase.csv"
    #crews    =  mainPath + path + r"\Report View of CREW STATUS TABLE - ONCE DAILY 0800.csv" 
    output   =  mainPath + r"\IHT Project\Data\Server\Output.csv"
    
    conn = connect("root","Code","localhost","iht_test")
    cursor = conn.cursor()
    
    pending_lines  = get_pending(cursor)    
    homebase_lines = get_homebase(cursor)
    crews_lines    = get_crews(cursor)
    
    write_file_forecast(output,pending_lines,homebase_lines,crews_lines)

if __name__ == '__main__':
    start()