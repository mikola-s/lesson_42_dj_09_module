$('#id_photo').change( (event) => {
    $('#id_label').text(event.target.files[0].name)
})