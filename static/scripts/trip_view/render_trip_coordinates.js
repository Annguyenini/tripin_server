const requestTripCoordiantes =async()=>{
    console.log('request coordiante')
    const response = await fetch (TRIP_COORDINATES_URL(TOKEN),{
        method:'GET',
    })
    const coordinates = await response.json()
    return coordinates.coordinates
}

const renderTripCoordinates = async (map) => {
    console.log('render coord')
    const coordinates = await requestTripCoordiantes();
    console.log('coordinates',coordinates)
    map.flyTo([coordinates[0].latitude, coordinates[0].longitude], 18, {
        duration: 3.5,
        easeLinearity: 0,  // closer to 0 = more ease in/out, smoother
        animate: true,
    });
    // draw line
    const latlngs = coordinates.map(c => [c.latitude, c.longitude]);
    L.polyline(latlngs, {
        color: '#1a1a1a',
        weight: 2,
        dashArray: '6, 6',
    }).addTo(map);

    // draw dots
    coordinates.forEach(c => {
        L.circleMarker([c.latitude, c.longitude], {
            radius: 6,
            color: '#f0f0ec',
            fillColor: '#1a1a1a',
            fillOpacity: 1,
            weight: 2,
        }).addTo(map);
    });

    // trigger first media render
    const zoom = Math.floor(map.getZoom());
    renderTripMedias(map, zoom);
    hideLoading();
};