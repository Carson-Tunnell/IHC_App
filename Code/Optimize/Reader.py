# This program goes through and processes input files for optimization
# used as a helper class for Optimize_Driver

#opens file from path given
#looks through pending requests and finds ones that are valid
#returns a list of valid requests
#returns reqID,Lat,Long of a given request
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
        splat = line.split(',')
        if splat[type_index] == "Crew__ Type 1":
            valid_list.append([int(splat[reqID_index]),float(splat[lat_index]),float(splat[lng_index])])

    return valid_list

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
        valid_dict[int(splat[resID])] = (float(splat[lat_index]),float(splat[lng_index]))
    return valid_dict

# Returns list of all available crew resID's
# Crews returned are only ones that are "Crew_ Type 1" and "Available"
# **More criterias can be added here to filter out crews more correctly**
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
        splat = line.split(',')
        if splat[res_status] == "Available" and splat[crew_type] == "Crew_ Type 1":
            valid_list.append(int(splat[resID]))

    return valid_list

# Used for Debugging
def write_file(filename, pending,homebase,crews):
    file = open(filename,'w+')
    #Creates the header the file needs for the distance program
    file.write("ResID,DestIncID,StartingPtLat,StartingPtLong,DestinationLat,DestinationLong,DistanceInMi,TimeInSec,CrewToSend\n")

    for i in pending:
        for j in crews:
            line_write = str(j) + "," + str(i[0]) + "," + str(homebase[j][0]) + "," + str(homebase[j][1]) + "," + str(i[1])  + "," + str(i[2]) + "\n"
            file.write(line_write)
    file.close()
    print("Written to: ", filename)

if __name__ == '__main__':
    print("Running Reader")

    pending  = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Reduced_Pending.csv"
    homebase = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\HomeBase.csv"
    crews    = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Reduced_Crews.csv"
    output   = r"C:\Users\Carson\OneDrive\College CSU\Year 4\Summer 2018\IHT Project\Data\Optimize Data\Output.csv"
    
    pending_lines = read_pending(pending)
    homebase_lines = read_homebase(homebase)
    crews_lines = read_crews(crews)
    
    print("Pending len: " , len(pending_lines))
    print("Crews: ", len(crews_lines))
    #ResID	DestIncID	StartingPtLat	StartingPtLong	DestinationLat	DestinationLong	DistanceInMi	TimeInSec	CrewToSend
    #CrewID,FireID,    HomeLat,        HomeLong,       FireLat,        FireLong, 
    write_file(output,pending_lines,homebase_lines,crews_lines)
    #20 Fires
    #30 Crews
    #When using reduced Data sets
    #num_crews = len(crews_lines)
    #num_incident = len(pending_lines)
    #(address + 1) % Length
    #circle_array = [num_crews][0]
    #Code To write to file and create distances for all points
