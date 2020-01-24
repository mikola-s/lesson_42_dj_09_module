//for input file

//случайное число в диапазоне от min до max с точность 2 знака после запятой
function getRndFloatInRange(digitPastDot, max, min=0) {
    let ranc = 10**digitPastDot
    let getRndIntInRange = (maxInt, minInt=0) => Math.floor(Math.random() * (maxInt - minInt + 1) + minInt)

    return (getRndIntInRange(max*ranc, min*ranc)/ranc).toFixed(digitPastDot)
}

function randomInt(min, max){
    return Math.floor(Math.random() * (max - min + 1) + min)
}

$('#id_photo').change( (event) => {
    $('#id_label').text(event.target.files[0].name)
    let str = event.target.files[0].name.replace('icons8-', '').replace('.svg','')
    $('#id_name').attr('value', str)
    $('#id_price').attr('value', getRndFloatInRange(2,50, 1000))
    $('#id_count').attr('value', randomInt(10, 100))
})