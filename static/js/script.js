/* Navbar script */

$(".dropdown-trigger").dropdown();

$(document).ready(function () {
    $('.sidenav').sidenav();
});

$(document).ready(function () {
    $('.parallax').parallax();
});

$(document).ready(function () {
    $('input.autocomplete').autocomplete({
        data: {
            "Apple": null,
            "Microsoft": null,
            "Google": 'https://placehold.it/250x250'
        },
    });
});