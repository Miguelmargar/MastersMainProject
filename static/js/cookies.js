function getCount() {
    var count = 0
    for (var i = 0; i < 5; i++) {
        if (localStorage.getItem("cookie" + i.toString())) {
            count++;
        }
    };
    return count;
};


function saveCookie() {
    var count = getCount();

    if (count < 4) {
        if (googleData != undefined) {

            var variableList = [googleData["routes"][0]["legs"][0]["start_address"],
                googleData["routes"][0]["legs"][0]["end_address"], htmlDepArr];

            var flag = false;
            for (var i = 0; i < count; i++) {
                var cookieCheck = JSON.parse(localStorage.getItem("cookie" + i.toString()));

                if (cookieCheck[0] === variableList[0] && cookieCheck[1] === variableList[1] && cookieCheck[2] ===
                variableList[2]) {
                    flag = true;
                }
            };
            if (flag == false) {
                localStorage.setItem("cookie" + count.toString(), JSON.stringify(variableList));
                count++;
                alert("This search has been ADDED to your Favourites");
                showFavs();
                setTimeout(function() {
                    if (getCount() > 0) {
                        $("div.favourites").slideDown("slow");
                        var elemPos = $("div#favs").position();
                        window.scrollTo(elemPos.left, elemPos.top - 75);
                    }
                    else {
                        alert("Favourites list is empty");
                        window.scrollTo(0,0);
                    }},
                    950);
            }
            else {
                alert("This specific trip is already in your favourites");
            }
        }
        else {
            alert("No previous search available to save, please perform a search to save it");
        }
    }
    else {
        alert("Apologies you have reached the max of 4 saved searches");
    };
}


function removeCookie(num) {
    localStorage.removeItem("cookie" + num.toString());
    showFavs();
    setTimeout(function() {
        if (getCount() > 0) {
            $("div.favourites").slideDown("slow");
        }
        else {
            alert("Favourites list is empty");
            window.scrollTo(0,0);
        }},
        950);
}


function showFavs() {

    $('div').remove(".favButt");

    for (var i = 0; i < 5; i++) {
        if (localStorage.getItem("cookie" + i.toString())) {

            var favData = JSON.parse(localStorage.getItem("cookie" + i.toString()));

            var favButt = document.createElement("div");
            favButt.setAttribute("class", "favButt");

            var favOri = document.createElement("div");
            favOri.setAttribute("class", "favOri");
            favOri.setAttribute("onclick", "loadFav(" + i.toString() + ")");
            var ori = document.createElement("p");
            var oriText = document.createTextNode(favData[0]);
            ori.appendChild(oriText);
            favOri.appendChild(ori);
            favButt.appendChild(favOri);

            var favDest = document.createElement("div");
            favDest.setAttribute("class", "favDest");
            favDest.setAttribute("onclick", "loadFav(" + i.toString() + ")");
            var dest = document.createElement("p");
            var destText = document.createTextNode(favData[1]);
            dest.appendChild(destText);
            favDest.appendChild(dest);
            favButt.appendChild(favDest);

            var favRem = document.createElement("div");
            favRem.setAttribute("class", "favRem");
            var rem = document.createElement("p");
            rem.setAttribute("onclick", "removeCookie(" + i.toString() + ")")
            var remText = document.createTextNode("Remove");
            rem.appendChild(remText);
            favRem.appendChild(rem);
            favButt.appendChild(favRem);

            document.getElementById("favs").appendChild(favButt);
        }
    };
    var elemPos = $("#belowops").position();

    if ($("div.favourites").css("display") != "none") {
        window.scrollTo(elemPos.left, elemPos.top -50);
        $("div.favourites").slideUp("slow");
    }
    else if ($("div.favourites").css("display") == "none") {
        if (getCount() == 0) {
            alert("No Search in Favourites to Show. Please Make a Search to Then Save It");
            window.scrollTo(0,0);
        }
        else {
            $("div.favourites").slideDown("slow");
            window.scrollTo(elemPos.left, elemPos.top -50);
        }
    };
}


function loadFav(num) {

    backAmenities = undefined;
    $("div.options").slideUp("slow");
    $("div.amenities").slideUp("slow");
    $("div#ftco-loader").addClass('show');

    var cookie = JSON.parse(localStorage.getItem("cookie" + num.toString()));

    displayNowTimeDate();

    $.getJSON($SCRIPT_ROOT + '/directions', {
            postA: cookie[0],
            postB: cookie[1],
            htmlDepArr: cookie[2],
            htmlTime: document.getElementById("time").value,
            htmlDate: document.getElementById("date").value,
        },
    //  Response from the back end
        function(response) {
            googleData = response['gooData'];
            intermediateStops = response['interstops'];
            disruptions = response["disruptions"];

            showOptions();
        })
}


function getCookie(num) {
    var cookie = JSON.parse(localStorage.getItem("cookie" + num.toString()));

    if (cookie != undefined) {
        console.log(cookie);
    }
    else {
        alert("error");
    }
}
