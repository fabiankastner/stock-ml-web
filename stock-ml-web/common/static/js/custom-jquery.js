$(document).ready(function() {
    $('#highbutton').click( function(event){
        $('#highbutton').removeClass('btn-outline-primary').addClass('btn-primary');

        $('#lowbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#openbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#closebutton').removeClass('btn-primary').addClass('btn-outline-primary');
    });

    $('#lowbutton').click( function(event){
        $('#lowbutton').removeClass('btn-outline-primary').addClass('btn-primary');

        $('#highbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#openbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#closebutton').removeClass('btn-primary').addClass('btn-outline-primary');
    });

    $('#openbutton').click( function(event){
        $('#openbutton').removeClass('btn-outline-primary').addClass('btn-primary');

        $('#highbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#lowbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#closebutton').removeClass('btn-primary').addClass('btn-outline-primary');
    });

    $('#closebutton').click( function(event){
        $('#closebutton').removeClass('btn-outline-primary').addClass('btn-primary');

        $('#highbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#lowbutton').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#openbutton').removeClass('btn-primary').addClass('btn-outline-primary');
    });

});