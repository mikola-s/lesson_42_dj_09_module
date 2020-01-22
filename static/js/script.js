// for navbar
$("li.nav-item a.nav-link[href='" + location.pathname + "']").addClass('active')



$(".card-img-top").map(function () {
    $(this).on('load', function () {
        console.log('111')
    })
})
