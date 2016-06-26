WS_SERVER_HOSTNAME = window.location.hostname
if(WS_SERVER_HOSTNAME == "") {
    WS_SERVER_HOSTNAME = "fraybentos.heart"
}
WS_SERVER_PORT = 8081

$(function() {
    
    var connecting = false
    var connected = false
    var attitude = $.flightIndicator('#attitude', 'attitude', {roll:0, pitch:0, size:800, showBox:false});
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
                message = JSON.parse(evt.data);

                headingValue = message.heading;
                pitchValue = message.pitch;
                rollValue = -message.roll;

                heading.setHeading(headingValue);
                attitude.setRoll(pitchValue);
                attitude.setPitch(rollValue);

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



