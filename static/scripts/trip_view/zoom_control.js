const allowedZooms = [7,8,9,10,11,12,13,14,15, 20, 21, 22];
let _zoomRef = null
const zoomControl =(map)=>{
    map.on('zoom', () => {
    const zoomraw = map.getZoom()
    const zoom = Math.floor(zoomraw)
    if(zoom===_zoomRef)return
    else if (allowedZooms.includes(zoom)){
        _zoomRef= zoom
        console.log(zoom)  
        renderTripMedias(map, zoom)
    }
})
}