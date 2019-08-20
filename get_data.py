import requests, datetime, pymysql, sys, difflib, sys
from operator import itemgetter
from datetime import date, time, timedelta
from tweepy import OAuthHandler, API, Cursor
from passw import *
from geopy.distance import geodesic
# from geopy.distance import great_circle
from darksky import forecast


class Stops:

    def __init__(self):
        self.goahead = ["17", "17a", "18", "33a", "33b", "45a", "45b", "59", "63", "63a", "75", "75a", "76", "76a",
                        "102", "104", "111", "114", "161", "175", "184", "185", "220", "236", "238", "239", "270"]

    def get_direct_goo(self, postA, postB, secs, depArrTime):

        self.postA = postA
        self.postB = postB
        self.secs = secs
        if depArrTime == "dep":
            depArrTime = '&departure_time='
        elif depArrTime == "arr":
            depArrTime = '&arrival_time='


        url ='https://maps.googleapis.com/maps/api/directions/json?alternatives=true&transit_mode=bus&'

        req = requests.get(url + 'origin=' + self.postA +'&destination=' + self.postB + depArrTime + secs
                           +'&sensor=false&mode=transit&key=' + google_key) # google_key imported from
        # passw.py in local

        return req.json()


    def lat_lon(self, busNo, head_sign, goolat, goolon):

        user = 'root'
        password = db_key
        host = '127.0.0.1'
        database = 'research'

        try:
            con = pymysql.connect(host=host, database=database, user=user, password=password)
        except Exception as e:
            sys.exit(e)

        lat = round(float(goolat), 4)
        lon = round(float(goolon), 4)

        query = """SELECT distinct stop_lat, stop_lon, stop_id, stop_name 
                FROM research.stops, research.stop_times
                WHERE research.stop_times.bus_stop_number = research.stops.stop_id 
                    and research.stop_times.bus_number = %s
                    and research.stop_times.headsign = %s
                    and ((stop_lat BETWEEN %s and %s) and (stop_lon BETWEEN %s and %s));"""

        cur = con.cursor()
        cur.execute(query, (busNo, head_sign, lat-0.001, lat+0.001, lon-0.001, lon+0.001), )
        data = cur.fetchall()
        if len(data) < 1:
            cur.execute(query, (busNo, head_sign, lat-0.003, lat+0.003, lon-0.003, lon+0.003), )
            data = cur.fetchall()
        cur.close()

        return tuple(data)


    def filter_name(self, stops_list, google_name):

        final = ()

        ratio = 0
        for stop in stops_list:
            stop_ratio = difflib.SequenceMatcher(None, stop[3], google_name).ratio()
            if stop_ratio > ratio:
                ratio = stop_ratio
                final = stop

        return final


    def db_query3(self, head_sign, bus_no, stop_noA, stop_noB, diff):

        user = 'root'
        password = db_key
        host = '127.0.0.1'
        database = 'research'

        try:
            con = pymysql.connect(host=host, database=database, user=user, password=password)
        except Exception as e:
            sys.exit(e)

        query = """SELECT research.stop_times.bus_stop_number, research.stop_times.stop_sequence, 
        research.stop_times.headsign, research.trips.trip_id
            FROM research.stop_times, research.trips
            WHERE research.stop_times.trip_id = research.trips.trip_id
                and stop_times.headsign = %s 
                and stop_times.bus_number = %s 
                and (bus_stop_number = %s or bus_stop_number = %s)"""

        cur = con.cursor()
        cur.execute(query, (head_sign, bus_no, stop_noA, stop_noB),)
        cur.close()
        data = cur.fetchall()

        final = []

        for i, value in enumerate(data):
            if i == 0:
                final.append(value)
            else:
                if value[1] - final[0][1] == diff:
                    final.append(value)

        return tuple(final)


    def db_query4(self, bus_no, head_sign, seqA, seqB, tripid):

        user = 'root'
        password = db_key
        host = '127.0.0.1'
        database = 'research'

        try:
            con = pymysql.connect(host=host, database=database, user=user, password=password)
        except Exception as e:
            sys.exit(e)

        query = """SELECT research.stops.stop_lat, research.stops.stop_lon, research.stop_times.bus_stop_number, 
                research.stop_times.stop_sequence, research.stop_times.headsign, research.stop_times.bus_number,
                research.stops.stop_name 
                FROM research.stop_times, research.stops, research.trips
                WHERE research.stop_times.bus_stop_number = research.stops.stop_id
                    and research.trips.trip_id = research.stop_times.trip_id
                    and research.stop_times.bus_number = %s 
                    and research.stop_times.headsign = %s 
                    and (research.stop_times.stop_sequence between %s AND %s)
                    and research.stop_times.trip_id = %s
                """

        cur = con.cursor()
        cur.execute(query, (bus_no, head_sign, seqA, seqB, tripid),)
        cur.close()
        # sorted(student_tuples, key=itemgetter(2))
        ordered = sorted(list(cur.fetchall()), key=itemgetter(3))
        return ordered


    def fin(self, goo_data):

        route_keys = [goo_data["routes"][i].keys() for i, k in enumerate(goo_data["routes"])]
        all_opts = []
        for i in range(len(route_keys)):
            option = []
            for j in range(len(goo_data["routes"][i]["legs"][0]["steps"])):

                if "transit_details" in goo_data["routes"][i]["legs"][0]["steps"][j] and goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["line"]["vehicle"]["type"] == "BUS":

                    dep_stop = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["departure_stop"]["name"].strip()
                    arr_stop = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["arrival_stop"]["name"].strip()
                    bus_no = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["line"]["short_name"].strip()
                    head_sign = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["headsign"].strip()
                    num_stops = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["num_stops"]

                    latA = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["departure_stop"]["location"]["lat"]
                    lonA = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["departure_stop"]["location"]["lng"]

                    latB = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["arrival_stop"]["location"]["lat"]
                    lonB = goo_data["routes"][i]["legs"][0]["steps"][j]["transit_details"]["arrival_stop"]["location"]["lng"]

                    print("Option:", i, "leg", j)
                    print("Details from google:")
                    print("dep_stop:", dep_stop)
                    print("arr_stop:", arr_stop)
                    if bus_no in self.goahead:
                        print("bus_no:", bus_no, "**FROM GOAHEAD**")
                    else:
                        print("bus_no:", bus_no)
                    print("num_stops: ", num_stops)
                    print("head_sign:", head_sign)
                    print("lat/lon A:", latA, lonA)
                    print("lat/lon B:", latB, lonB)
                    print()

                    print("1st Query - lat_lon ----------------------")
                    print("stopA")
                    oneA = self.lat_lon(bus_no, head_sign, latA, lonA)
                    print(oneA)
                    print()
                    print("stopB")
                    oneB = self.lat_lon(bus_no, head_sign, latB, lonB)
                    print(oneB)
                    print()

                    if len(oneA) > 0 and len(oneB) > 0:
                        print("filter 1st query by name -----------------------")
                        print("stopA")
                        twoA = self.filter_name(oneA, dep_stop)
                        print(twoA)
                        print()
                        print("stopB")
                        twoB = self.filter_name(oneB, arr_stop)
                        print(twoB)
                        print()

                        if twoA and twoB:
                            print("Query 3 - get seq and direction id -------------")
                            # Stop A and stop B here have to be the ones from our filters not from google
                            three = self.db_query3(head_sign, bus_no, twoA[2], twoB[2], num_stops)
                            print(three)
                            print()

                            if len(three) == 2:
                                print("Query 4 - obtain intermediate stops ------------")
                                # Pass only the 1st two stops given by previous query
                                four = self.db_query4(bus_no, head_sign, three[0][1], three[1][1], three[0][3])
                                option.append(four)
                                print(four)
                                print()

                            else:
                                print("ERROR: query 3 does not have 2 items - it has:", len(three), "items")
                                pass
                        else:
                            print("ERROR: length of twoA:", len(twoA), "length of twoB:", len(twoB))
                            pass
                    else:
                        print("ERROR: length of oneA is", len(oneA), "length of oneB:", len(oneB))
                        pass

                    print()
            all_opts.append(option)
            print("-------------------------------------------------------------------------------------------")
        return all_opts


    def getSeconds(self, date, time):
        self.date = date
        self.time = time + ":00"

        currentTimeDate = datetime.datetime.now()

        if len(self.date) < 1:
            self.date = currentTimeDate.strftime("%Y-%m-%d")
        if len(self.time) < 4:
            self.time = currentTimeDate.strftime("%H:%M:%S")


        dateTime = self.date + " " + self.time
        timeObj = datetime.datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")

        seconds = round(timeObj.timestamp())

        return str(seconds)


    def getAmenities(self, type, list):

        self.type = type
        self.list = list

        self.finalAmenities = []

        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'

        for option in self.list:
            opList = []
            for leg in option:
                for stop in leg:
                    location = str(stop[0])+","+str(stop[1])
                    req = requests.get(url + "location=" + location + "&radius=50&type=" + self.type
                                       + "&fields=formatted_address,geometry,name&key=" + google_key)

                    if req.json()["status"] == "OK":
                        opList.append(req.json()["results"])

            self.finalAmenities.append(opList)

        return self.finalAmenities


    def notification_check(self, googData):

        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        auth_api = API(auth)

        end_date = datetime.datetime.utcnow() - timedelta(days=1)
        tweetlist=[]

        for i in range(len(googData["routes"])):
            option = []
            for j in range(len(googData["routes"][i]["legs"][0]["steps"])):

                if "transit_details" in googData["routes"][i]["legs"][0]["steps"][j] and googData["routes"][i]["legs"][0]["steps"][j]["transit_details"]["line"]["vehicle"]["type"] == "BUS":

                    route = googData["routes"][i]["legs"][0]["steps"][j]["transit_details"]["line"]["short_name"].strip()

                    for status in Cursor(auth_api.user_timeline, id="@dublinbusnews").items():
                        if "#DBSvcUpdate" in status.text:
                            if ("#DB" + route.lower()) in status.text and status.text not in option:
                                option.append(status.text)
                        if status.created_at < end_date:
                            break
            tweetlist.append(option)

        return(tweetlist)


    def get_stop_distances(self, stops):
        self.stops = stops

        distances = []

        for option in self.stops:
            option_list = []
            for leg in option:
                leg_list = []

                for i, stop in enumerate(leg):
                    try:
                        stopA = (float(stop[0]), float(stop[1]))
                        stopB = (float(leg[i + 1][0]), float(leg[i + 1][1]))
                        stopNo = leg[i + 1][2]
                        distance = geodesic(stopA, stopB).km * 1000
                        leg_list.append((stopNo[-5:].lstrip("0"), distance))
                    except:
                        break

                option_list.append(leg_list)
            distances.append(option_list)
        return distances


    def get_seconds_model(self, goog_data):
        self.goog_data = goog_data

        seconds_final = []

        for i, op in enumerate(self.goog_data["routes"]):
            seconds_options = []
            for j, leg in enumerate(self.goog_data["routes"][i]["legs"][0]["steps"]):

                if "transit_details" in goog_data["routes"][i]["legs"][0]["steps"][j] and goog_data["routes"][i][
                    "legs"][0]["steps"][j]["transit_details"]["line"]["vehicle"]["type"] == "BUS":

                    time = self.goog_data["routes"][i]["legs"][0]["steps"][j]["transit_details"][
                        "departure_time"]["text"]

                    if time[-2:] == "pm":
                        if time[:-2].split(":")[0] != "12":
                            hour = (int(time[:-2].split(":")[0]) + 12) * 60 * 60
                        else:
                            hour = int(time[:-2].split(":")[0]) * 60 * 60
                    else:
                        hour = int(time[:-2].split(":")[0]) * 60 * 60

                    mins = int(time[:-2].split(":")[1]) * 60
                    seconds = hour + mins

                    seconds_options.append(seconds)

            seconds_final.append(seconds_options)
        return seconds_final


    def weather_get(self, date, time):
        self.date = date
        self.time = time + ":00"

        resultdic = {}

        # format - 2018-10-24T19:06:32
        try:
            time = self.date + "T" + self.time
            weather = forecast("0f94f1e529d8359a54cc753b465312d7", 53.344505, -6.258602, time=time)
            resultdic["temperature"] = ((weather.temperature - 32)*5)/9
            resultdic["rain"] = weather.precipIntensity
            resultdic["humidity"] = weather.humidity
            return resultdic
        except IOError as e:
            return ("ERROR_WEATHER_GET", e)



    def weekend_holiday(self, date):

        import holidays

        #Date format - 2018-01-01 (y-m-d) - string
        return_dic = {}
        holidays = holidays.Ireland()
        try:
            if datetime.datetime.strptime(date, '%Y-%m-%d').weekday() > 4:
                return_dic["weekend"] = 1
            else:
                return_dic["weekend"] = 0

            if datetime.datetime.strptime(date, '%Y-%m-%d') in holidays:
                return_dic["holiday"] = 1
            else:
                return_dic["holiday"] = 0
            return return_dic
        except ValueError as e:
            return ("ERROR_WEEKEND_HOLIDAY",e)


    def run_model(self, stoplist, time, precipitation, temperature, humidity, holiday, weekend):

        import pickle
        import numpy as np
        import csv
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVR

        self.stoplist = stoplist


        #Import model and scalers
        zonedict = {}
        with open('stopzones.csv') as zone_csv:
            csv_reader = csv.reader(zone_csv, delimiter=',')
            for row in csv_reader:
                zonedict[str(row[0])] = str(row[1])

        output_list = []

        for i,option in enumerate(self.stoplist):
            option_list = []
            
            for p,leg in enumerate(option):
                leg_list = []
                
                
                for j,stop in enumerate(leg):
                    
                    try:
                        zone = zonedict[str(stop[0])]
                    except:
                        zone = 6
                    target_scaler = 'tar_scaler_{0}.sav'.format(zone)
                    feature_scaler = 'feat_scaler_{0}.sav'.format(zone)
                    model = "model_zone_{0}.sav".format(zone)

                    #Load files
                    tar_scaler = pickle.load(open(target_scaler, 'rb'))
                    feat_scaler = pickle.load(open(feature_scaler, 'rb'))
                    model = pickle.load(open(model, 'rb'))

                    dist = stop[1]
            
                    to_scale=np.array([time[i][p], precipitation, temperature, humidity, dist, holiday, weekend])
                   
                    to_scale = to_scale.reshape(1, -1)
                    to_predict= feat_scaler.transform(to_scale)
                    
                    prediction = abs(tar_scaler.inverse_transform(model.predict(to_predict)))
                    
                    leg_list.append(prediction)

                option_list.append(int(sum(leg_list)/100))
            output_list.append(int(sum(option_list)))
        
        return output_list

