
var msgValid = "is good!";
var submit = document.getElementById("submit");

var ids = {
    "login": "ala",
    "password": "aaaaaaaa",
    "password2": "aaaaaaaa",
    "firstname": "Ala",
    "lastname": "Makota",
    "sex": "F",
    "photo": "an1.png",
    "email": "ala@mako.ta"
};




var goodFields = {
    "login": false,
    "password": false,
    "password2": false,
    "firstname": false,
    "lastname": false,
    "sex": false,
    "photo": false,
    "email": false
};


var regexDict = new Map();

regexDict.set("login", [/^[a-z]{3,12}$/, "small Latin letters, length between 3 and 12"]);
regexDict.set("password", [/.{8,}/, "at least 8 characters long"]);
regexDict.set("password2", [/.+/, "passwords have to match"]);

regexDict.set("firstname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols, has to start with the capital letter"]);
regexDict.set("lastname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols, has to start with the capital letter"]);
regexDict.set("sex", [/^[M,F]{1}$/, "either Male or Female"]);

regexDict.set("photo", [/.+/, "a file has to be chosen (PNG or JPG)"]);
regexDict.set("email", [/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/, "no email provided"]);




function availCheck(id, value) {


    let xhr = new XMLHttpRequest();
    let host = 'https://infinite-hamlet-29399.herokuapp.com/check/' + value;
    xhr.onreadystatechange = function () {
        let DONE = 4;
        let OK = 200;
        if (xhr.readyState == DONE) {
            if (xhr.status == OK) {

                let response = JSON.parse(xhr.responseText);

                console.info(response)

                trackField(id, (response[value] === "available"), " username is taken")


            }
        }
    };
    xhr.open('GET', host, true);
    xhr.send(null);
    console.log(id + ": request sent to:", host);
}


function passwordsMatchCheck() {

    p1 = document.getElementById("password").value
    p2 = document.getElementById("password2").value

    console.info(p1, p2)

    if (p2 == "") {
        return true
    } else {

        return p1 == p2
    }

}


function validateField(id, value) {

    console.info("Validating " + id + " field...")

    var [regex, msgInvalid] = regexDict.get(id)


    // For everything: Check RegEx
    if (regex.test(value)) {

        console.info(id + ": passes regex")


        // For passwords: check if passwords match
        if ((id == "password2") || (id == "password")) {
            trackField(id, passwordsMatchCheck(), "passwords have to match")
        }


        // For photo: check JPG or PNG
        else if (id == "photo") {

            trackField(id, (value.endsWith(".jpg") || value.endsWith(".png")), msgInvalid)

        }


        // For login: check if availible on https://infinite-hamlet-29399.herokuapp.com/check/<username>
        else if (id == "login") {

            var host = "http://" + window.location.hostname;

            if (host.endsWith(".herokuapp.com")) {
                availCheck(id, value)
            } else {
                trackField(id, true, msgInvalid)
            }

        }

        else trackField(id, true, msgInvalid)

    }

    else trackField(id, false, msgInvalid)





}

function trackField(id, isGood, msgInvalid) {

    goodFields[id] = isGood
    msg = id.charAt(0).toUpperCase() + id.slice(1) + ": " + (isGood ? msgValid : msgInvalid);

    console.info(msg);
    var alertField = document.getElementById(id + "-alert");
    alertField.innerHTML = msg;
    alertField.className = isGood ? "alert-good" : "flashes";



    if (id != "photo") {
        checkIcon(id, isGood)
    }

    checkIfAllGood();
}


function checkIcon(id, isGood) {

    iconID = id + "-icon"
    var iconElem = document.getElementById(iconID)
    iconElem.setAttribute("hidden", "")


    errorID = id + "-error"
    var errorElem = document.getElementById(errorID)

    goodID = id + "-good"
    var goodElem = document.getElementById(goodID)


    if (isGood) {
        // console.info( id + ": " + )
        errorElem.setAttribute("hidden", "")
        goodElem.removeAttribute("hidden")
    } else {
        errorElem.removeAttribute("hidden")
        goodElem.setAttribute("hidden", "")
    }

}

function checkIfAllGood() {

    console.info(goodFields);

    var allGood = (
        (goodFields["login"] == true) &&
        (goodFields["password"] == true) &&
        (goodFields["password2"] == true) &&
        (goodFields["firstname"] == true) &&
        (goodFields["lastname"] == true) &&
        (goodFields["sex"] == true) &&
        (goodFields["photo"] == true) &&
        (goodFields["email"] == true)
    )


    if (allGood == true) {
        console.info("Submit is now active!")
        submit.removeAttribute("disabled");
    } else {
        submit.setAttribute("disabled", "");
    }
}






function attach_events() {

    var keys = Object.keys(ids)
    console.info(keys)

    keys.forEach(listen)

    function listen(elemID) {

        var element = document.getElementById(elemID);
        
        // if (elemID != "photo") {
        //     var mockup = ids[elemID];
        //     element.value = mockup;
        //     console.info("Mockup for " + elemID + ": " + mockup);
        //     validateField(elemID, element.value);
        // }

        element.addEventListener("change", function (ev) {
            validateField(elemID, element.value)
        })
        console.info("Added listener to ", elemID, "\n")


    }

}

attach_events();