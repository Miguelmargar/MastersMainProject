import re
from flask import Flask, redirect, render_template, request, jsonify
from datetime import datetime
from get_data import *
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    todayObj = datetime.datetime.now()
    today = todayObj.strftime("%Y-%m-%d")
    max = todayObj + timedelta(days=30)
    maxDate = max.strftime("%Y-%m-%d")

    return render_template('index.html', today=today, maxDate=maxDate)

@app.route("/directions", methods=['GET', 'POST'])
def directions():
    postA = request.args.get('postA')
    postB = request.args.get('postB')
    frontDepArr = request.args.get('htmlDepArr')
    frontTime = request.args.get('htmlTime')
    frontDate = request.args.get('htmlDate')


    intermediate = Stops()
    secs = intermediate.getSeconds(frontDate, frontTime)
    get_goo_data = intermediate.get_direct_goo(postA, postB, secs, frontDepArr)
#     jsonObj = intermediate.get_direct_goo(postA, postB, secs, frontDepArr)
    interStops = intermediate.fin(get_goo_data)
    global full
    notifications = intermediate.notification_check(get_goo_data)
    full = {"interstops": interStops, "gooData": get_goo_data, "disruptions": notifications}

    return jsonify(full)

@app.route("/amenities", methods=['GET', 'POST'])
def Amenities():
    frontAmenities = request.args.get('htmlAmenities')

    interAmenities = Stops()
    amenitiesList = interAmenities.getAmenities(frontAmenities, full["interstops"])

    return jsonify(amenitiesList)


@app.route('/events', methods=["GET", "POST"])
def events():
    print(request)

    cardlist = []
    site = requests.get('https://dublin.ie/whats-on/').text
    soupsite = BeautifulSoup(site, 'lxml')
    cards = soupsite.findAll("article", {"class": "event card"})

    for i in cards:
        templist = []
        try:
            templist.append(i.find("h2").text)  # Name
            templist.append(
                re.search("url\(\'(.*)\'\)", i.find("div", {"class": "img"})["style"]).group(1))  # Image URL
            templist.append(i.find("a", {"class": "read-more"})["href"])  # Link to more info
            templist.append(i.find("div", {"class": "summary"}).find("p").text.split(".")[0] )
            cardlist.append(templist)
        except:
            cardlist.append("ERROR")
    return jsonify(cardlist)


if __name__ == '__main__':
    app.run(debug=True)


#set FLASK_APP=app.py
#set FLASK_ENV=development