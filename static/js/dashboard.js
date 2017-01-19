$(document).ready(function(){
    var url = window.location.href;
    $('ul.nav.nav-sidebar a').filter(function() {
        return this.href == url;
    }).parent().addClass('active');

});