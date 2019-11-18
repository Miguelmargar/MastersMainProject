var dublin = {lat: 53.349605, lng:-6.264175 };

// Geolocation variable
var pos;

// Date and time of search
var dateTime;

// Locations entered by the user
var posA = {};
var posB = {};

// Data returned by the google call in the back end
var googleData;

// Data of intermediate stops worked out in the back end with google data
var intermediateStops;

// Time prediction data
var prediction;

// Data for tweeter disruption responses
var disruptions;

// To Work out today's date and now's time for search form
var nowDayTime;
var htmlDepArr;
var hrs;
var mins;

// To give a height to the map and the chart for each option
var mapChartHeight;

// To take the response from the google places nearby search
var backAmenities;

// when an specific option is clicked or chosen
var num;


// When a map needs to be refreshed
function refreshMap(num) {

    if (num === undefined) {
        map = new google.maps.Map(
              document.getElementById('map'), {zoom: 12, center: dublin,
              zoomControl: true,
              mapTypeControl: true,
              mapTypeControlOptions: {
              style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
              },
              scaleControl: true,
              streetViewControl: true,
              streetViewControlOptions: {
              position: google.maps.ControlPosition.RIGHT_CENTER
              },
              rotateControl: true,
              fullscreenControl: true
            });
    } else {
        map = new google.maps.Map(
              document.getElementById('map'+num.toString()), {zoom: 12, center: dublin,
              zoomControl: true,
              mapTypeControl: true,
              mapTypeControlOptions: {
              style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
              },
              scaleControl: true,
              streetViewControl: true,
              streetViewControlOptions: {
              position: google.maps.ControlPosition.RIGHT_CENTER
              },
              rotateControl: true,
              fullscreenControl: true
            });
    }
}


// Display current time and current date in search form
function displayNowTimeDate() {

    nowDayTime = new Date();
    hrs = nowDayTime.getHours().toString();
    mins = nowDayTime.getMinutes().toString();
    if (mins.length < 2) {
        mins = "0" + mins;
    }
    if (hrs.length < 2) {
        hrs = "0" + hrs;
    }
    document.querySelector("#time").value = hrs + ":" + mins;
    document.querySelector("#date").valueAsDate = nowDayTime;
}


// use geolocation from browser
function geolocation() {
    // Try HTML5 geolocation.
    if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
        };

    }, function() {
    handleLocationError(true, infoWindow, map.getCenter());
    });
    } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
        }
}


// Initialize and add the map
function initMap(num) {
    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer();

    refreshMap(num);

    // start the user's geolocations-------------------------------------------
    infoWindow = new google.maps.InfoWindow;

    // Try HTML5 geolocation.
    if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
        pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
        };

        infoWindow.setPosition(pos);
        infoWindow.setContent('<div class="infoWin">You are here</div>');
        infoWindow.open(map);
        map.setCenter(pos);
    }, function() {
    handleLocationError(true, infoWindow, map.getCenter());
    });
    } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
        }
    directionsDisplay.setMap(map);

    };// initMap()


// Handle geolocation errors
function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
                      'Error: The Geolocation service failed.' :
                      'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
    }


// Take input from origin of trip
function stopA(){
    // AutoComplete------------------------------------------------------------
    var input = document.getElementById('start');

    var dublinBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(53.1235, -6.5021),
      new google.maps.LatLng(53.4872, -6.0209));

    var defaultBounds = {
        bounds: dublinBounds,
        strictBounds: true
        };

    var autocomplete = new google.maps.places.Autocomplete(input, defaultBounds);

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
      var place = autocomplete.getPlace();
      var lat = place.geometry.location.lat();
      var lng = place.geometry.location.lng();
      posA = {
      	lat: lat,
      	lng: lng
      	};
        });
    }

// Take input from Destination of trip
function stopB(){
    // AutoComplete------------------------------------------------------------
    var input = document.getElementById('end');

    var dublinBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(53.1235, -6.5021),
      new google.maps.LatLng(53.4872, -6.0209));

    var defaultBounds = {
        bounds: dublinBounds,
        strictBounds: true
        };

    var autocomplete = new google.maps.places.Autocomplete(input, defaultBounds);

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
      var place = autocomplete.getPlace();
      var lat = place.geometry.location.lat();
      var lng = place.geometry.location.lng();
      posB = {
      	lat: lat,
      	lng: lng
      	};
        });
    }

// Draw the polylines from the back end google maps directions api call
function draw_poly(googleData, option) {
    if (option === undefined) {
        option = 0;
    }
    for (var i = 0; i < googleData['routes'][option]['legs'][0]['steps'].length; i++) {
//        IF its walking draw polyline with a certain color
        if (googleData['routes'][option]['legs'][0]['steps'][i]['travel_mode'] == 'WALKING') {
            var poli = new google.maps.Polyline({
                  path: google.maps.geometry.encoding.decodePath
                  (googleData['routes'][option]['legs'][0]['steps'][i]['polyline']['points']),
                  geodesic: true,
                  strokeColor: '#ff6600',
                  strokeOpacity: 0.5,
                  strokeWeight: 5
                });
                poli.setMap(map);
        }
//        If its by bus draw the polyline with a certain colour
        else if (googleData['routes'][option]['legs'][0]['steps'][i]['travel_mode'] == 'TRANSIT') {
            var poli = new google.maps.Polyline({
                  path: google.maps.geometry.encoding.decodePath
                  (googleData['routes'][option]['legs'][0]['steps'][i]['polyline']['points']),
                  geodesic: true,
                  strokeColor: '#0000cc',
                  strokeOpacity: 0.5,
                  strokeWeight: 5
                });
                poli.setMap(map);
        }
    }
}


// Draw the intermediate stops
function draw_markers(intermediateStops, option) {
    if (option === undefined) {
        option = 0;
    }
    var infowindow = new google.maps.InfoWindow();
    for (var i = 0; i < intermediateStops[option].length; i++) {
        for (var j = 0; j < intermediateStops[option][i].length; j++) {

            var location = {lat: intermediateStops[option][i][j][0], lng: intermediateStops[option][i][j][1]};
            var marker = new google.maps.Marker({animation: google.maps.Animation.DROP, position: location, map: map});

            var name = intermediateStops[option][i][j][6];
            var going = intermediateStops[option][i][j][4];
            var stopNum = intermediateStops[option][i][j][2].slice(-4);

            var contentString = '<div class="infoWin">' +
                                '<p class="detail">STOP NAME: ' + name + '</p>' +
                                '<p class="detail">GOING TO: ' + going + '</p>' +
                                '<p class="detail">STOP NO: ' + stopNum + '</p>' +
                                '</div>';

            google.maps.event.addListener(marker, 'click', (function(contentString, marker, i) {
                return function() {
                    infowindow.setContent(contentString.toString());
                    infowindow.open(map, marker);
                }
            })(contentString, marker, i));
        }
    }
}

// Create the html to show the different options with minimal info
function showOptions() {
	console.log(googleData);

    $('div').remove(".opbutt");
    $('div').remove(".opinfo");

    if (googleData) {
         const routes = googleData['routes'];
         const display_routes = new Set();

         for (let i = 0; i < routes.length; i++) {
             const steps = routes[i]['legs'][0]['steps'];

             let lines = [];
             for (let j = 0; j < steps.length; j++) {
                 const step = steps[j];

                 if (step['travel_mode'] === 'TRANSIT') {
                     lines.push(step['transit_details']['line']['short_name']);
                 }
             }
             lines = lines.join('/');
             display_routes.add(lines);
         }
         
         
        var countOps = 0;
//        Build the options buttons
        for (var i = 0; i < googleData['routes'].length; i++) {

            var addAlert = false;

            var opbutt = document.createElement("div");
            opbutt.setAttribute("class", "opbutt");
            opbutt.setAttribute("onClick", "chooseOption(" + i.toString() + ")");

            var opInfo = document.createElement("div");
            opInfo.setAttribute("class", "opinfo");
            opInfo.setAttribute("id", "opinfo"+i.toString());

            var allSteps = document.createElement("div");
            allSteps.setAttribute("class", "allsteps");
            allSteps.setAttribute("id", "allSteps"+i.toString())

            var topAllSteps = document.createElement("div");
            topAllSteps.setAttribute("class", "topAllSteps");

            var from = document.createElement("p");
            var fromText = document.createTextNode("FROM: " + googleData['routes'][i]['legs'][0]["start_address"]);
            from.appendChild(fromText);

            var to = document.createElement("p");
            var toText = document.createTextNode("TO: " + googleData['routes'][i]['legs'][0]["end_address"]);
            to.appendChild(toText);

            topAllSteps.appendChild(from);
            topAllSteps.appendChild(to);

            allSteps.appendChild(topAllSteps);


            var miniMap = document.createElement("div");
            miniMap.setAttribute("class", "minimap");
            miniMap.setAttribute("id", "map"+i.toString());

            var opGraph = document.createElement("div");
            opGraph.setAttribute("class", "graph");
            opGraph.setAttribute("id", "graph"+i.toString());
            var chart = document.createElement("canvas");
            chart.setAttribute("id", "mychart"+i.toString());
            opGraph.appendChild(chart);

            var alert = document.createElement("div")
            alert.setAttribute("class", "alert");

            var indiv1 = document.createElement("div");
            indiv1.setAttribute("class", "indivleft");
            var time = document.createElement("p");
            var timetext = document.createTextNode(googleData['routes'][i]['legs'][0]['duration']['text']);
            time.appendChild(timetext);
            indiv1.appendChild(time);
            opbutt.appendChild(indiv1);
	    
            var indiv2 = document.createElement("div");
            indiv2.setAttribute("class", "indivmid");
            var time = document.createElement("p");
            var timetext = document.createTextNode(googleData['routes'][i]['legs'][0]['departure_time']['text'] + " to " + googleData['routes'][i]['legs'][0]['arrival_time']['text']);
            time.appendChild(timetext);
            indiv2.appendChild(time);
            opbutt.appendChild(indiv2);

            var indiv3 = document.createElement("div");
            indiv3.setAttribute("class", "indivright");
            var buses = document.createElement("p");
            var allBuses = [];
            for (var j = 0; j < googleData['routes'][i]['legs'][0]['steps'].length; j++ ) {

                var step = document.createElement("p");
                var stepOff = document.createElement("p");
                var alertMessP = document.createElement("p");

                if (googleData['routes'][i]['legs'][0]['steps'][j]['travel_mode'] == 'WALKING' && j ==
                googleData['routes'][i]['legs'][0]['steps'].length - 1) {
                    var instruction = document.createTextNode
                    (googleData['routes'][i]['legs'][0]['steps'][j]['html_instructions']);
                    step.appendChild(instruction);
                    allSteps.appendChild(step);
                }
                else if (googleData['routes'][i]['legs'][0]['steps'][j]['travel_mode'] == 'WALKING') {
                    var instruction = document.createTextNode
                    (googleData['routes'][i]['legs'][0]['steps'][j]['html_instructions'] + " Bus Stop");
                    step.appendChild(instruction);
                    allSteps.appendChild(step);
                }
                else if (googleData['routes'][i]['legs'][0]['steps'][j]['travel_mode'] == 'TRANSIT') {
                    var instruction = document.createTextNode
                    ("Get On Bus " +  googleData['routes'][i]['legs'][0]['steps'][j]['transit_details']
                    ['line']['short_name'] + googleData['routes'][i]['legs'][0]['steps'][j]['html_instructions']
                    .substring(3))

                    var off = document.createTextNode
                    ("Get Off At " + googleData['routes'][i]['legs'][0]['steps'][j]['transit_details']
                    ['arrival_stop']['name'] + " Bus Stop");

                    step.appendChild(instruction);
                    allSteps.appendChild(step);
                    stepOff.appendChild(off);
                    allSteps.appendChild(stepOff);

                    allBuses.push(googleData['routes'][i]['legs'][0]['steps'][j]['transit_details']['line']
                    ['short_name']);
                }
                 if (disruptions[i][j] != undefined && disruptions[i][j].length > 0) {
                     var alertMessage = document.createTextNode(disruptions[i][j]);
                     alertMessP.appendChild(alertMessage);
                     alert.appendChild(alertMessP);
                     addAlert = true;
                 }
            };
            var timetext = document.createTextNode(allBuses.join(" / "));
            buses.appendChild(timetext);
            indiv3.appendChild(buses);
            opbutt.appendChild(indiv3);

            opInfo.appendChild(miniMap);
            opInfo.appendChild(allSteps);
            opInfo.appendChild(opGraph);
            if (addAlert == true) {
                opInfo.appendChild(alert);
            }
//            Filter the options to show the ones that use the bus number given in search form and display first on map
//            that fits the chosen bus number
            var routeNeeded = document.getElementById("route").value.toUpperCase();
            if (routeNeeded.length > 0) {
                if (allBuses.includes(routeNeeded) == true) {
                    document.getElementById('ops').appendChild(opbutt);
                    document.getElementById('ops').appendChild(opInfo);
                    countOps++;
                    if (countOps == 1) {
                        chooseOption(i);
                    }
                } else {
                    document.getElementById('ops').appendChild(opbutt);
                    document.getElementById('ops').appendChild(opInfo);
                }
            }
//            If no specific bus number input in search form show all options in list and display 1st on map
            else if (routeNeeded.length < 1) {
                document.getElementById('ops').appendChild(opbutt);
                document.getElementById('ops').appendChild(opInfo);
                countOps++;
                if (countOps == 1) {
                    chooseOption(i);
                }
            }
        }
        if (countOps < 1) {
            window.alert("The Quickest Options Don't Use the Bus You Specified! - however see below for" +
                "ALTERNATIVES to your search! Otherwise please try searching again without a different bus number")
            chooseOption(0);
        }
        $("div.options").slideDown("slow");
        $("div.amenities").slideDown("slow");

    } else {
        document.getElementById('ops').style.display = 'none';
    }
}


// Check the date and time from form against now
function checkDateAndTime() {

    formTime = document.getElementById("time").value;
    formDate = document.getElementById("date").value;

    formSeconds = (new Date(formDate + " " + formTime + ":00" ).getTime() / 1000) + 60;
    nowDayTime = new Date();
    nowDayTimeSeconds = nowDayTime.getTime() / 1000;

    if (formSeconds > (nowDayTimeSeconds + 2764800)) {
        alert("Please enter a date within 31 days");
        return false;
    }
    else {
        if (htmlDepArr == "dep") {
                if (formSeconds + 60 < nowDayTimeSeconds) {
                        alert("Sorry, the time you entered is in the past!");
                    } else {
                        return true;
                    }
            }
            else if (htmlDepArr == "arr") {

                if (googleData) {
                    var delayed = 0;
                    for (var i = 0; i < googleData["routes"].length; i++) {
                        var gooDepTime = googleData["routes"][i]["legs"][0]["departure_time"]["value"];
                        if (gooDepTime < nowDayTimeSeconds) {
                            delayed++;
                        } else {
                            return true;
                        }
                    };
                    if (delayed > 0) {
                        alert("The entered time may be too late for some of the options shown below");
                        return true;
                    }
                }
                else {
                    return true;
                }
            }
        }
    }


// display the selected steps and other details
function showSteps(num) {

//    checkDateAndTime();

    if ( $("#opinfo"+num.toString()).css("display") != "none") {
            $("#opinfo"+num.toString()).slideUp("slow");
        }
    else {
    $(".opinfo").not("#opinfo"+num.toString()).slideUp("slow");
    $("#opinfo"+num.toString()).slideDown("slow", opsDetailsSize);
    };
}


// Choose the option number and display it
function chooseOption(num) {

	createChart(num);
    initMap(num);
    showSteps(num);
    draw_markers(intermediateStops, num);
    draw_poly(googleData, num);
    if (backAmenities) {
        drawAmenitiesMarkers();
    };

    if (num == 0) {
//        window.scrollTo(0, 800);
        $('html, body').animate({
            scrollTop: ($('#belowops').offset().top)
            },500);
    } else if (num == 1) {
//        window.scrollTo(0, 1120);
        $('html, body').animate({
            scrollTop: ($('#belowops').offset().top)
            },500);
    } else if (num == 2) {
        window.scrollTo(0, 1120);
    } else if (num == 3) {
        window.scrollTo(0, 1150);
    };
    $("div#ftco-loader").removeClass('show');
}


// Obtain if the form wants to search by departure time or arrival time
function getDepArr() {
    var radioButton = document.getElementsByName("deparr");

    for (var i = 0; i < radioButton.length; i++) {
        if (radioButton[i].checked) {
            htmlDepArr = radioButton[i].value;
        }
    }
    return htmlDepArr;
}


// Send the directions from/to to the back end to obtain the intermediate stops for each option
function ajaxInt() {

    backAmenities = undefined;

//    Check that the user has input a value otherwise use the geolocation coordinates
    var origin = document.getElementById("start").value;

    if (origin.length > 0) {
        postA = origin;
    } else if (origin.length < 1) {
        postA = pos['lat'].toString() + "," + pos['lng'].toString();
    }

    var dest = document.getElementById("end").value;

    if (dest.length < 1) {
        alert("PLEASE INPUT A DESTINATION")
    } else {
        getDepArr();
        if (checkDateAndTime() == true) {
            $("div.options").slideUp("slow");
            $("div.amenities").slideUp("slow");
            setTimeout(function() {$("div#ftco-loader").addClass('show');}, 500);
            //    Ajax pass variables to Flask back end
                $.getJSON($SCRIPT_ROOT + '/directions', {
                    postA,
                    postB: dest,
                    htmlDepArr,
                    htmlTime: document.getElementById("time").value,
                    htmlDate: document.getElementById("date").value,
                },
            //  Response from the back end
                function(response) {
                    googleData = response['gooData'];
                    intermediateStops = response['interstops'];
                    prediction = response['prediction'];
                    disruptions = response["disruptions"];
                    showOptions();
                });
            }
        }
    }


// Create chart for each option
function createChart(num) {
    var chart = document.getElementById("mychart"+num.toString());
    Chart.defaults.global.defaultFontColor = "white";
    var time = googleData['routes'][num]['legs'][0]['duration']['value'] / 60
    var best = time - 8;
    var main = time;
    var worst = time + 15;

    var data = {
        labels: ["Best Case", "Main Prediction", "Worst Case"],
        datasets: [{
            label: "Minutes",
            backgroundColor: "white",
            borderColor: "black",
            data:[best, main, worst],
        }]
    };

    var options = {
        maintainAspectRatio: false,
        title: {
              display: true,
              text: 'Bus Arrival Time',
              fontSize: 12,
            },
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Cases",
                        fontSize: 12,
                        fontColor: "white"
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: best,
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Prediction Times",
                        fontSize: 12
                    }
                }]
            },
        }
        Chart.Bar(chart, {
          options: options,
          data: data
        });
}


// Markers for each option's amenities
function drawAmenitiesMarkers() {
    opId = $("div.opinfo");
    var count = 0;
    for (var i = 0; i < opId.length; i++) {
        if (opId[i].style.display == 'block') {
            var id = opId[i].getAttribute("id");
            count++;
        }
    }
    if (count > 0) {
        var opNeeded = parseInt(id.slice(-1));
    } else if (count == 0) {
        var opNeeded = 0;
    }
    var infowindow = new google.maps.InfoWindow();
    for (var i = 0; i < backAmenities[opNeeded].length; i++) {

        var location = {lat: backAmenities[opNeeded][i][0]["geometry"]["location"]["lat"], lng:
        backAmenities[opNeeded][i][0]["geometry"]["location"]["lng"]};
        var image = "https://img.icons8.com/ios-filled/50/000000/marker.png";
        var marker = new google.maps.Marker({
            animation: google.maps.Animation.DROP,
            position: location,
            map: map,
            icon: image});

        var name = backAmenities[opNeeded][i][0]["name"];
        if (backAmenities[opNeeded][i][0].hasOwnProperty("opening_hours")){
            var open = (backAmenities[opNeeded][i][0]["opening_hours"]["open_now"] == true) ? "Yes":"No";
        } else {
            var open = "Not Known"
        }
        var addr = backAmenities[opNeeded][i][0]["vicinity"];

        var contentString = '<div class="infoWin">' +
                            '<p class="detail">NAME: ' + name + '</p>' +
                            '<p class="detail">OPEN NOW: ' + open + '</p>' +
                            '<p class="detail">ADDRESS: ' + addr + '</p>' +
                            '</div>';

        google.maps.event.addListener(marker, 'click', (function(contentString, marker, i) {
            return function() {
                infowindow.setContent(contentString.toString());
                infowindow.open(map, marker);
            }
        })(contentString, marker, i));
    }
}


// Get google data for each amenity for each option
function ajaxAmen() {

    opId = $("div.opinfo");
    for (var i = 0; i < opId.length; i++) {
        if (opId[i].style.display == 'block') {
            var id = opId[i].getAttribute("id");
        }
    };
    if (id != undefined) {
        var opNeeded = parseInt(id.slice(-1));
        showSteps(opNeeded);
    } else {
        var opNeeded = 0;
    };
    var radioButton = document.getElementsByName("amenities");

    for (var i = 0; i < radioButton.length; i++) {
            if (radioButton[i].checked) {
                var htmlAmenities = radioButton[i].value;
            }
        };

    if (intermediateStops.length > 1) {
        $("div#ftco-loader").addClass('show');
        $.getJSON($SCRIPT_ROOT + '/amenities', {
            htmlAmenities,
        },
        //  Response from the back end
        function(response) {
            backAmenities = response;
            chooseOption(opNeeded);
        });
    }
    else {
        alert("No intermediate stops - Buses used may not be from GoAhead rather than Dublin Bus");
        $('html, body').animate({
            scrollTop: ($('#belowops').offset().top)
        },500);
    }
}


// fix the size of the options details divs
function opsDetailsSize() {
    var mapChartHeight = $("div.allsteps:visible").height();
    $("div.minimap:visible").height(mapChartHeight);
    $("div.graph:visible").height(mapChartHeight);
}


// Event listeners
$(window).load(displayNowTimeDate);

$(window).resize(opsDetailsSize);



