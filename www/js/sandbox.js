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
});