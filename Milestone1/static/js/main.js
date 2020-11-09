
var msgValid = "is good!"
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

regexDict.set("login", [/^[a-z]{3,12}$/, "small Latin letters, length between 3 and 12"]);
regexDict.set("password", [/.{8,}/, "at least 8 characters long"]);
regexDict.set("password2", [/.+/, "passwords have to match"]);

regexDict.set("firstname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols, has to start with the capital letter"]);
regexDict.set("lastname", [/^[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+$/, "Latin and/or Polish symbols, has to start with the capital letter"]);
regexDict.set("sex", [/^[M,F]{1}$/, "either Male or Female"]);

regexDict.set("photo", [/.+/, "a file has to be chosen (PNG or JPG)"]);




function availCheck( id, value ) {


    let xhr = new XMLHttpRequest();
    let host = 'https://infinite-hamlet-29399.herokuapp.com/check/' + value;
    xhr.onreadystatechange = function() {
        let DONE = 4;
        let OK = 200;
        if (xhr.readyState == DONE) {
            if(xhr.status == OK) {

                let response = JSON.parse(xhr.responseText);

                console.info(response)

                trackField( id, (response[value] === "available"), " username is taken" )


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
    return p1 == p2
}


function validateField(id, value) {

    // console.info("Validating " + id + " field...")
    
    var [regex, msgInvalid] = regexDict.get(id)
    
 
    // For everything: Check RegEx
    if ( regex.test(value) ) {

        console.info(id + ": passes regex")
        
        
        // For passwords: check if passwords match
        if (id=="password2") {
            
            trackField( id, passwordsMatchCheck(), "passwords have to match" )
        }

        // For photo: check JPG or PNG
        else if (id=="photo") {

            trackField( id, (value.endsWith(".jpg") || value.endsWith(".png")), msgInvalid )
            
        }
        

        // For login: check if availible on https://infinite-hamlet-29399.herokuapp.com/check/<username>
        else if (id=="login") {

            var host = "http://"+window.location.hostname;

            if ( host.endsWith(".herokuapp.com") ) {
                availCheck( id, value )
            } else {
                trackField( id, true, msgInvalid )
            }

        }

        else trackField( id, true, msgInvalid )
        
    } 
    
    else trackField( id, false, msgInvalid )
    



    
}

function trackField( id, isGood, msgInvalid ) {
    
    goodFields.set( id, isGood )
    console.info( id + ": " + (isGood ? msgValid : msgInvalid) )
    if (id != "photo") {
        checkIcon( id, isGood )
    }
    
    checkIfAllGood();
}


function checkIcon( id, isGood ) {

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