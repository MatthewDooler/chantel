$(function() {
    var attitude = $.flightIndicator('#attitude', 'attitude', {roll:0, pitch:0, size:800, showBox:false});
    var heading = $.flightIndicator('#heading', 'heading', {heading:0, size:200, showBox:true});
    var variometer = $.flightIndicator('#variometer', 'variometer', {vario:-5, showBox:true});
    var airspeed = $.flightIndicator('#airspeed', 'airspeed', {showBox:true});
    var altimeter = $.flightIndicator('#altimeter', 'altimeter');

    // Update at 20Hz
    var increment = 0;
    setInterval(function() {
        
        heading.setHeading(0);
        attitude.setRoll(0);
        attitude.setPitch(0); // nose up/down
        
        // vertical speed
        variometer.setVario(0);
        
        airspeed.setAirSpeed(0);
        
        altimeter.setAltitude(223);
        altimeter.setPressure(1000);
        increment++;
    }, 50);

    // var sock = new SockJS('ws://127.0.0.1:8080');
    // sock.onopen = function() {
    //     console.log('open');
    // };
    // sock.onmessage = function(e) {
    //     console.log('message', e.data);
    // };
    // sock.onclose = function() {
    //     console.log('close');
    // };

    // sock.send('test');
    // sock.close();

    sock = new WebSocket("ws://localhost:8080/");
    // sock.send(message);
    // sock.close();
    sock.onopen = function(evt) {
        console.log('open');
    };
    sock.onclose = function(evt) {
        console.log("close\n");
    };
    sock.onmessage = function(evt) {
        console.log("message: " + evt.data + '\n');
    };
    sock.onerror = function(evt) {
        console.log('error: ' + evt.data + '\n');
        sock.close();
    };
});



