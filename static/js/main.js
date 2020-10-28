
var avail = false;
var submit = document.getElementById("submit");

var ids =  [
    "login",
    "password",
    "password2",
    "firstname",
    "lastname",
    "sex",
    "photo"
];


var goodFields = new Map();
ids.forEach(function (id, index) {
    goodFields.set( id, false );
})


var regexDict = new Map();

regexDict.set("login", [/[a-z]{3,12}/, "small Latin letters, length between 3 and 12"]);
regexDict.set("password", [/.{8,}/, "at least 8 characters long"]);
regexDict.set("password2", [/.+/, "must match Password"]);

regexDict.set("firstname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols"]);
regexDict.set("lastname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols"]);
regexDict.set("sex", [/^[M,F]{1}$/, "either Male or Female"]);

regexDict.set("photo", [/.+/, "a file has to be chosen (PNG or JPG)"]);




function availCheck(username) {


    let xhr = new XMLHttpRequest();
    let host = 'https://infinite-hamlet-29399.herokuapp.com/check/' + username;
    xhr.onreadystatechange = function(){
        let DONE = 4;
        let OK = 200;
        if (xhr.readyState == DONE){
            if(xhr.status == OK){
                let response = JSON.parse(xhr.responseText);
                console.info(response)
                if (response[username] === "available"){
                    trackField( id, true, " is good!" )
                } else {
                    trackField( id, false, " is not available" )
                }

            } 
        }
    };
    xhr.open('GET', host, true);
    xhr.send(null);
    console.log("request sent to:", host);
}


function passwordsMatchCheck() {
    p1 = document.getElementById("password").value
    p2 = document.getElementById("password2").value
    return p1 == p2
}


function validateField(id, value) {

    // console.info("Validating " + id + " field...")
    
    // var isGood = false;
    var [regex, msg] = regexDict.get(id)
 
 
    // For everything: Check RegEx
    if ( regex.test(value) ) {
        
        
        // For passwords: check if passwords match
        if (id=="password" || id=="password2") {
            if (!passwordsMatchCheck()) {
                return trackField( id, false, msg )
            }
        }

        // For photo: check JPG or PNG
        if (id=="photo") {
            if (!(value.endsWith(".jpg") || value.endsWith(".png"))) {
                return trackField( id, false, msg )
            }
        }
        

        // For login: check if availible on https://infinite-hamlet-29399.herokuapp.com/check/<username>
        if (id=="login") {

            var host = "http://"+window.location.hostname;

            if ( host.endsWith(".herokuapp.com") ) {
                return availCheck(value)
            }

        }

    }
    

    return trackField( id, true, " is good!" )



    
}

function trackField( id, isGood, msg ) {
    
    goodFields.set( id, isGood )
    console.info(id + ": " + msg)
    if (id != "photo") {
        checkError( id, isGood )
    }
    
    checkIfAllGood();
}


function checkError( id, isGood ) {

    iconID = id+"-icon"
    var iconElem = document.getElementById( iconID )
    iconElem.setAttribute("hidden", "")
    

    errorID = id+"-error"
    var errorElem = document.getElementById( errorID )

    goodID = id+"-good"
    var goodElem = document.getElementById( goodID )
    
    
    if (isGood) {
        errorElem.setAttribute("hidden", "")
        goodElem.removeAttribute("hidden")
    } else {
        errorElem.removeAttribute("hidden")
        goodElem.setAttribute("hidden", "")
    }

}

function checkIfAllGood() {

    
    if (
        Array.from( goodFields.values() ).every( (state) => state == true ) 
    ) {
        console.info("Submit is now active!")
        submit.removeAttribute("disabled");
    } else {
        // console.info("Submit is not active :(")
        submit.setAttribute("disabled", "");
    }
}






function attach_events() {
    
    
    ids.forEach(loadListener);


    function loadListener( elemID, index ) {

        // var validateFunc = validations.get( elemID );

        var element = document.getElementById( elemID );

        element.addEventListener("change", function (ev) {
            // console.info("new value in", elemID, ":", element.value)
            // validateFunc( elemID, element.value )
            validateField( elemID, element.value )
        })
        
        
    }


}

attach_events();