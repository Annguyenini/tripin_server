const setTripData=( tripName, coverImage )=> {
    console.log(tripName,coverImage)
   if (coverImage) {
        const img = document.getElementById('trip-cover')
        
        img.onload = () => {
            img.style.display = 'block'
            document.getElementById('cover-no-image').style.display = 'none'
            // setDynamicBorder(img)  ← won't work without CORS headers on S3
        }
        img.onerror = () => console.error('failed:', coverImage)
        img.src = coverImage  // ← no crossOrigin
    } 
    else {
        document.getElementById('trip-cover').style.display = 'none'
        document.getElementById('cover-no-image').style.display = 'flex'
        document.getElementById('no-image-trip-name').textContent = tripName || 'TRIPPING'

    }
    if (tripName)    document.getElementById('trip-name').textContent = tripName
    document.getElementById('cover-qr').innerHTML = ''
    new QRCode(document.getElementById('cover-qr'), {
        text: window.location.href,
        width: 72,
        height: 72,
        colorDark: '#1a1a1a',
        colorLight: '#f0f0ec',
        correctLevel: QRCode.CorrectLevel.M
    })
}
const setUpTripCover =async()=>{
    const res = await requestTripData(TOKEN)
    
    const trip_data = res.trip_data
    console.log(res)
    setTripData(trip_data.trip_name,trip_data.image)
}
setUpTripCover()