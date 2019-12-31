WS_SERVER_HOSTNAME = window.location.hostname
if(WS_SERVER_HOSTNAME == "") {
    WS_SERVER_HOSTNAME = "localhost"
}
WS_SERVER_PORT = 8081

var pingInterval= 5000
var pingRequest = Date.now()
var pingResponse = pingRequest
var lastPingResponse = pingResponse
var connecting = false
var connected = false
var sock = null

$(function() {
    
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

                if(typeof message.ping !== 'undefined') {
                    pingRequest = message.ping
                    pingResponse = Date.now()
                    lastPingResponse = pingResponse
                    updateLatency()
                } else {
                    headingValue = message.heading;
                    pitchValue = message.roll;
                    rollValue = -message.pitch;
                    camImageUri = "img/8FnqQTs.jpg"

                    cam.setCamHeading(headingValue);
                    cam.setCamRoll(rollValue);
                    cam.setCamPitch(pitchValue);

                    // TODO: only call when we actually want to update the image (otherwise it will be too much traffic)
                    // cam.setCamImage(message.cam_image_pitch, message.cam_image_roll, message.cam_image_heading, message.cam_image_uri);

                    heading.setHeading(headingValue);
                    attitude.setRoll(pitchValue);
                    attitude.setPitch(pitchValue);

                    variometer.setVario(0); // vertical speed
                    airspeed.setAirSpeed(0);
                    altimeter.setAltitude(223);
                    altimeter.setPressure(1000);

                    for (var throttleId in message.throttle) {
                        setActualThrottle(throttleId, message.throttle[throttleId])
                    }
                }
            };
            sock.onerror = function(evt) {
                console.log('error: ' + evt.data + '\n');
                sock.close();
            };
        }
    }, 1000);

    // Send ping messages to the server to calculate latency
    setInterval(ping, pingInterval)
    setInterval(updateLatency, 500);

});

function ping() {
    if(connected && !connecting) {
        sock.send(JSON.stringify({"ping": Date.now()}));
    }
}

function restart() {
    if(connected && !connecting) {
        sock.send(JSON.stringify({"restart": []}));
    }
}

function shutdown() {
    if(connected && !connecting) {
        sock.send(JSON.stringify({"shutdown": []}));
    }
}

function updateLatency() {
    pingLatency = (pingResponse - pingRequest) / 2
    bestCaseEstimatedLatency = (Date.now() - lastPingResponse - pingInterval) / 2 // this will normally be a bit better/lower than the true latency, but if it's higher that's a problem
    latency = Math.max(pingLatency, bestCaseEstimatedLatency)
    if(latency < 1000) {
        $(".latency-value").html(Math.round(latency)+" ms")
    } else if(latency < 60000) {
        $(".latency-value").html(Math.round(latency/1000)+" s")
    }
}

var minThrottle = 0
var maxThrottle = 100
var desiredThrottleValues = {0:0, 1:0, 2:0, 3:0}
var actualThrottleValues = {0:0, 1:0, 2:0, 3:0}

var listenToKeyPresses = true
$(document).keypress(function(e) {
    increaseCharacter = 61
    reduceCharacter = 45
    if(listenToKeyPresses) {
        switch(e.which) {
            case increaseCharacter:
                for (var throttleId in desiredThrottleValues) {
                    changeDesiredThrottle(throttleId, 1)
                }
                break
            case reduceCharacter:
                for (var throttleId in desiredThrottleValues) {
                    changeDesiredThrottle(throttleId, -5)
                }
                break;
        }
        sock.send(JSON.stringify({"throttle": desiredThrottleValues}))
    }
});

function changeDesiredThrottle(throttleId, increment) {
    desiredThrottleValues[throttleId] = Math.max(minThrottle, Math.min(maxThrottle, desiredThrottleValues[throttleId]+increment))
    renderDesiredThrottle(throttleId, desiredThrottleValues[throttleId])
}

function renderDesiredThrottle(throttleId, value) {
    var throttleEl = $(".throttle"+throttleId)
    var barEl = throttleEl.find(".progress-bar")
    var offset = desiredThrottleTickOffset(throttleEl.height(), barEl.height(), value)
    var notchEl = barEl.find(".notch")
    listenToKeyPresses = false
    notchEl.animate({bottom: offset}, 100, function() {
        listenToKeyPresses = true
    })
}

var actualThrottleAnimating = [false, false, false, false]
function setActualThrottle(throttleId, value) {
    actualThrottleValues[throttleId] = value
    var throttleEl = $(".throttle"+throttleId)
    var originalHeight = throttleEl.find(".progress-bar").height()
    var newHeight = ((throttleEl.height()/100.0)*value)
    var heightChange = newHeight - originalHeight
    if(heightChange >= 1 || heightChange <= -1) {
        if(!actualThrottleAnimating[throttleId]) {
            actualThrottleAnimating[throttleId] = true
            throttleEl.find(".progress-bar").animate(
                {
                    height: newHeight
                }, {
                    duration: 300,
                    progress: function(animation, progress, remainingMs) {
                        var barElHeight = $(animation.elem).height()
                        var offset = desiredThrottleTickOffset(throttleEl.height(), barElHeight, desiredThrottleValues[throttleId])
                        throttleEl.find(".progress-bar .notch").css("bottom", offset)
                    },
                    done: function() {
                        actualThrottleAnimating[throttleId] = false
                    }
                }
            )
        }
    }
}

function desiredThrottleTickOffset(throttleElHeight, barElHeight, value) {
    return (((throttleElHeight/100.0)*value) + 1.5) - barElHeight
}

function simple_setActualThrottle(throttleId, value) {
    actualThrottleValues[throttleId] = value
    var throttleEl = $(".throttle"+throttleId)
    var newHeight = ((throttleEl.height()/100.0)*value)
    throttleEl.find(".progress-bar").css("height", newHeight)
    var offset = (((throttleEl.height()/100.0)*desiredThrottleValues[throttleId]) + 1.5) - newHeight
    throttleEl.find(".progress-bar .notch").css("bottom", offset)
    
}
