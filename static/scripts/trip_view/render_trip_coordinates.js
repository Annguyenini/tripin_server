const requestTripCoordiantes =async()=>{
    const response = await fetch (TRIP_COORDINATES_URL(TOKEN),{
        method:'GET',
    })
    const coordinates = await response.json()
    return coordinates.coordinates
}

const renderTripCoordinates = async (map) => {
    const coordinates = await requestTripCoordiantes()
    console.log(coordinates)
    map.flyTo({
        center: [coordinates[0].longitude, coordinates[0].latitude],
        zoom: 13,
        duration: 5000
    })

    // points
    map.addSource('trip-coordinates', {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: coordinates.map(e => ({
                type: 'Feature',
                geometry: { type: 'Point', coordinates: [e.longitude, e.latitude] },
                properties: { name: e.time_stamp }
            }))
        }
    })
    map.addLayer({
        id: 'trip-points-layer',
        type: 'circle',
        source: 'trip-coordinates',
        paint: {
            'circle-radius': 8,
            'circle-color': '#1a1a1a',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#f0f0ec',
        }
    })

    // line
    map.addSource('trip-line', {
        type: 'geojson',
        data: {
            type: 'Feature',
            geometry: {
                type: 'LineString',
                coordinates: coordinates.map(e => [e.longitude, e.latitude])
            }
        }
    })
    map.addLayer({
        id: 'trip-line-layer',
        type: 'line',
        source: 'trip-line',
        paint: {
            'line-color': '#1a1a1a',
            'line-width': 2,
            'line-dasharray': [2, 2],
        }
    })
}