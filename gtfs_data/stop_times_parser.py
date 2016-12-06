ride_file = open("one_ride.txt","w+")

with open("boston/stop_times.txt") as f:
    ride_file.write('"trip_id","arrival_time","departure_time","stop_id","stop_sequence","stop_headsign","pickup_type","drop_off_type"\n')
    for line in f:
        if "31724879" in line:
             ride_file.write(line)