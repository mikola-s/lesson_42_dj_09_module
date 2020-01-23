//for input file

function randomInt(min, max){
    return Math.floor(Math.random() * (max - min + 1) + min)
}

$('#id_photo').change( (event) => {
    $('#id_label').text(event.target.files[0].name)
    let str = event.target.files[0].name.replace('icons8-', '').replace('.svg','')
    $('#id_name').attr('value', str)
    $('#id_price').attr('value', randomInt(50, 1000))
    $('#id_count').attr('value', randomInt(10, 100))
})