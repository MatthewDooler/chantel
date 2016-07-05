WS_SERVER_HOSTNAME = window.location.hostname
if(WS_SERVER_HOSTNAME == "") {
    WS_SERVER_HOSTNAME = "localhost"
}
WS_SERVER_PORT = 8081

$(function() {
    
    var connecting = false
    var connected = false
    var cam = $.flightIndicator('#cam', 'cam', {roll:0, pitch:0, heading:0, width:600, height:300, showBox:false});
    $('#cam').find('div.instrument').css({height : 350, width : 820});
    var attitude = $.flightIndicator('#attitude', 'attitude', {roll:0, pitch:0, size:418, showBox:true});
    var heading = $.flightIndicator('#heading', 'heading', {heading:0, size:200, showBox:true});
    var variometer = $.flightIndicator('#variometer', 'variometer', {vario:-5, showBox:true});
    var airspeed = $.flightIndicator('#airspeed', 'airspeed', {showBox:true});
    var altimeter = $.flightIndicator('#altimeter', 'altimeter');

    // Check connection every second (to reconnect if it's closed)
    setInterval(function() {
        if(!connected && !connecting) {
            connecting = true
            console.log("connecting")
            sock = new WebSocket("ws://"+WS_SERVER_HOSTNAME+":"+WS_SERVER_PORT.toString()+"/");
            // sock.send(message);
            // sock.close();
            sock.onopen = function(evt) {
                console.log('open');
                $("#connection-state").toggleClass("connected", true).toggleClass("disconnected", false).html("Connected to " + WS_SERVER_HOSTNAME + ":"+WS_SERVER_PORT.toString())
                connected = true
                connecting = false
            };
            sock.onclose = function(evt) {
                console.log("close\n");
                $("#connection-state").toggleClass("connected", false).toggleClass("disconnected", true).html("Disconnected from " + WS_SERVER_HOSTNAME + ":"+WS_SERVER_PORT.toString())
                connected = false
                connecting = false
            };
            sock.onmessage = function(evt) {
                console.log(evt.data);
                message = JSON.parse(evt.data);

                headingValue = message.heading;
                pitchValue = message.roll;
                rollValue = -message.pitch;
                camImageUri = "img/8FnqQTs.jpg"

                cam.setCamHeading(headingValue);
                cam.setCamRoll(rollValue);
                cam.setCamPitch(pitchValue);

                // TODO: only call when we actually want to update the image (otherwise it will be too much traffic)
                cam.setCamImage(message.cam_image_pitch, message.cam_image_roll, message.cam_image_heading, message.cam_image_uri);

                heading.setHeading(headingValue);
                attitude.setRoll(pitchValue);
                attitude.setPitch(pitchValue);

                variometer.setVario(0); // vertical speed
                airspeed.setAirSpeed(0);
                altimeter.setAltitude(223);
                altimeter.setPressure(1000);
            };
            sock.onerror = function(evt) {
                console.log('error: ' + evt.data + '\n');
                sock.close();
            };
        }
    }, 1000);

});

var minThrottle = 0
var maxThrottle = 100
var desiredThrottleValues = {0:0, 1:0, 2:0, 3:0}
var actualThrottleValues = {0:0, 1:0, 2:0, 3:0} // TODO: adjust these based on server metrics

$(document).keypress(function(e) {
    increaseCharacter = 61
    reduceCharacter = 45
    switch(e.which) {
        case increaseCharacter:
            for (var throttleId in desiredThrottleValues) {
                changeDesiredThrottle(throttleId, 5)
            }
            break
        case reduceCharacter:
            for (var throttleId in desiredThrottleValues) {
                changeDesiredThrottle(throttleId, -5)
            }
            break;
    }
});

function changeDesiredThrottle(throttleId, increment) {
    desiredThrottleValue = Math.max(minThrottle, Math.min(maxThrottle, desiredThrottleValues[throttleId]+increment))
    desiredThrottleValues[throttleId] = desiredThrottleValue
    var throttleEl = $(".throttle"+throttleId)
    var offset = ((throttleEl.height()/100.0)*desiredThrottleValue) + 1.5
    throttleEl.find(".progress-bar .notch").css("bottom", offset)
    // TODO: send it to the server
}

