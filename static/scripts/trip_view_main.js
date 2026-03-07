
mapboxgl.accessToken = MAPBOX_TOKEN
const TOKEN = window.location.pathname.split('/').pop()

const STYLES = {
    dark:      'mapbox://styles/mapbox/dark-v11',
    streets:   'mapbox://styles/mapbox/streets-v12',
    satellite: 'mapbox://styles/mapbox/satellite-streets-v12',
};
const map = new mapboxgl.Map({
    container: 'map',
    style: STYLES.streets,
    center: [0, 20],
    zoom: 2,
    projection: 'globe',
});

map.on('style.load', () => {
    map.setFog({ color: '#0b0e14', 'high-color': '#1e2a3a', 'horizon-blend': 0.04 });
    renderTripCoordinates(map)
});

// Coords update
map.on('move', () => {
    const c = map.getCenter();
    document.getElementById('lng-val').textContent = c.lng.toFixed(4);
    document.getElementById('lat-val').textContent = c.lat.toFixed(4);
    document.getElementById('zoom-val').textContent = map.getZoom().toFixed(1);
});

// Click marker



// Style switcher
styleSwitcher(map)
// setup trip banner
setUpTripDataBanner()
renderTripMedias(map)