$('#id_photo').change( (event) => {
    let fileName = event.target.files[0].name
    $('#id_label').text(fileName)
    $('#id_img').attr('src', `/media/shop/product_image/${fileName}`)
    // console.log(`/media/shop/product_image/${event.target.files[0].name}`)
    // $('#id_img').
})