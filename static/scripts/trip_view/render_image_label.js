const requestTripMedias =async()=>{
    const response = await fetch (TRIP_MEDIAS_URL(TOKEN),{
        method:'GET',
    })
    const medias = await response.json()
    return medias.medias
}

const renderTripMedias= async (map) => {
    const medias = await requestTripMedias()
    console.log(medias)
    renderImageLabels(medias,map)
}
const renderImageLabels = (coordinates, map) => {
  if (!coordinates) return;

  coordinates.forEach((coord, index) => {
    // create polaroid-style marker element
    const el = document.createElement('div');
    el.className = 'img-marker';
    el.innerHTML = `<img src="${coord.media_path}" alt="trip photo" />`;

    // add to map
    new mapboxgl.Marker(el)
      .setLngLat([coord.longitude, coord.latitude])
      .addTo(map);
  });
};