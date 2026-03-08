const getCoorMaxMin=(lat,lng,radius)=>{
    const deltaLat = radius/111320
    const deltaLng = radius/ (111320 * Math.cos(lat * Math.PI / 180))
    return ({
        'minLat' : lat-deltaLat,
        'maxLat' : lat + deltaLat,
        'minLng' : lng - deltaLng,
        'maxLng' : lng +deltaLng,
    })}
const boxesOverlap=(a,b)=>{ 
    
  return !(
    a.maxLat < b.minLat ||
    a.minLat > b.maxLat ||
    a.maxLng < b.minLng ||
    a.minLng > b.maxLng
)}
const toRad = (deg) => deg * Math.PI / 180;
const toDeg =(rad)=> rad * 180 / Math.PI 
 const haversineDistance = (lat1, lng1, lat2, lng2) => {
    const R = 6371000; // Earth radius in meters
    const deltaLat = toRad(lat2 - lat1);
    const deltaLng = toRad(lng2 - lng1);

    const a = Math.sin(deltaLat / 2) ** 2 +
              Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
              Math.sin(deltaLng / 2) ** 2;

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // distance in meters
};

const CoorFromDistance=(lat, lon, distance_m, bearing_deg)=>{
    const R = 6371000  // Earth radius in meters

    const bearing = toRad(bearing_deg)

    const new_lat = Math.asin(
        Math.sin(toRad(lat)) * Math.cos(distance_m / R) +
        Math.cos(toRad(lat)) * Math.sin(distance_m / R) * Math.cos(bearing)
    )

    const new_lon = toRad(lon) + Math.atan2(
        Math.sin(bearing) * Math.sin(distance_m / R) * Math.cos(lat),
        Math.cos(distance_m / R) - Math.sin(lat) * Math.sin(new_lat)
    )
    
    return {latitude :toDeg(new_lat), longitude:toDeg(new_lon)}
}

 const TotalDistanceTravel=(coords_array)=>{
    let total_m = 0
    let last_coor = null
    for (const coord of coords_array){
        if(!last_coor){
            last_coor = coord
            continue
        }
        total_m += haversineDistance(coord[0],coord[1],last_coor[0],last_coor[1])
        last_coor =coord
    }
    return total_m
}


