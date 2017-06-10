$(function() {
  var $rad = $('#rad'),
      $obj = $('.obj'),
      deg = 0,
      rad = $rad.width() / 2;

  $obj.each(function(){
    var pos = $(this).data(),
        getAtan = Math.atan2(pos.x-rad, pos.y-rad),
        getDeg = (-getAtan/(Math.PI/180) + 180) | 0;
    // Read/set positions and store degree
    $(this).css({left:pos.x, top:pos.y}).attr('data-atDeg', getDeg);
  });

  (function rotate() {      
    $rad.css({transform: 'rotate('+ deg +'deg)'}); // Radar rotation
    $('[data-atDeg='+deg+']').stop().fadeTo(0,1).fadeTo(1700,0.2); // Animate dot at deg

    deg = ++deg % 360;      // Increment and reset to 0 at 360
    setTimeout(rotate, 25); // LOOP
  })();

});
