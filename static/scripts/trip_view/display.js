const _isMobile = () => /android|iphone|ipad/i.test(navigator.userAgent)

const _coorFromDistance=(lng,lat,distance_m, bearing_deg)=>{
    const R = 6371000  // Earth radius in meters

    const bearing = toRad(bearing_deg)

    const new_lat = Math.asin(
        Math.sin(toRad(lat)) * Math.cos(distance_m / R) +
        Math.cos(toRad(lat)) * Math.sin(distance_m / R) * Math.cos(bearing)
    )

    const new_lon = toRad(lng) + Math.atan2(
        Math.sin(bearing) * Math.sin(distance_m / R) * Math.cos(lat),
        Math.cos(distance_m / R) - Math.sin(lat) * Math.sin(new_lat)
    )
    
    return {latitude :toDeg(new_lat), longitude:toDeg(new_lon)}
}


const finalizeDisplayCoordinate=(lng,lat,map)=>{
    let dis_latitude
    let dis_longitude

    if (!_isMobile()) {
        const { latitude, longitude } = _coorFromDistance(lng,lat,100,270)
            dis_latitude = latitude
            dis_longitude = longitude
    }
    else {
        const { latitude, longitude } = _coorFromDistance(lng,lat,70,180)
        dis_latitude = latitude
        dis_longitude = longitude
    }
    
    map.flyTo({
            center: [dis_longitude, dis_latitude],
            zoom: 18,
            duration: 2000
    })
}