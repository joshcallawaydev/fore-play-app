/* Navbar script */

$(".dropdown-trigger").dropdown();

$(document).ready(function () {
    $('.sidenav').sidenav();
});

$(document).ready(function () {
    $('.parallax').parallax();
});

/* the below code is auto complete, test before deployment */
$(document).ready(function () {
    $('input.autocomplete').autocomplete({
        data: {
            "Apple": null,
            "Microsoft": null,
            "Google": 'https://placehold.it/250x250'
        },
    });
});

var slider = document.getElementById('hci-slider');
noUiSlider.create(slider, {
    start: [-5, 36],
    connect: true,
    step: 1,
    orientation: 'horizontal', // 'horizontal' or 'vertical'
    range: {
        'min': -5,
        'max': 36
    },
    format: wNumb({
        decimals: 0
    })
});