import requests, datetime, pymysql, sys, difflib, sys
from operator import itemgetter
from datetime import date, time, timedelta
from tweepy import OAuthHandler, API, Cursor
from passw import *
import re
from geopy.distance import geodesic


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

        user = db_user
        password = db_key
        host = db_host
        database = db_name

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

        user = db_user
        password = db_key
        host = db_host
        database = db_name

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

        user = db_user
        password = db_key
        host = db_host
        database = db_name

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
                            if (("#DB" + route.lower()) or ("#DB" + re.sub("\D", "",route.lower())) or "due to" or "Temporary") in status.text and status.text not in option:
                                option.append(status.text)
                        if status.created_at < end_date:
                            break
            tweetlist.append(option)

        return(tweetlist)

