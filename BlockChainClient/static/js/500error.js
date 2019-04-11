$(".full-screen").mousemove(function (a) {
    var b = $(".eye");
    var e = (b.offset().left) + (b.width() / 2);
    var f = (b.offset().top) + (b.height() / 2);
    var c = Math.atan2(a.pageX - e, a.pageY - f);
    var d = (c * (180 / Math.PI) * -1) + 180;
    b.css({
        "-webkit-transform": "rotate(" + d + "deg)",
        "-moz-transform": "rotate(" + d + "deg)",
        "-ms-transform": "rotate(" + d + "deg)",
        transform: "rotate(" + d + "deg)"
    })
});