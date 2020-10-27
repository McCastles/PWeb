function attach_events() {
    var firstname = document.getElementById("firstname");
    firstname.addEventListener("change", function (ev) {
        console.info("New Value ", firstname.value)
    })
}

attach_events();