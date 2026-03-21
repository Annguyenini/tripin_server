mapboxgl.accessToken = MAPBOX_TOKEN  // keep for tiles only

const TOKEN = window.location.pathname.split('/').pop()

const STYLES = {
    streets: `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
    dark:    `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
    satellite: `https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
}

showLoading('Loading Map')

const map = L.map('map', { zoomControl: false, minZoom: 4,   // ← can't zoom out past this
    maxZoom: 22, }).setView([20, 0], 10);

const tileLayer = L.tileLayer(STYLES.streets, {
    tileSize: 512,
    zoomOffset: -1,
    detectRetina: true,
    minZoom:4,
    maxZoom: 23,         // map can zoom to 22
    maxNativeZoom: 18,   // but reuse z18 tiles beyond that (just scaled up)
    keepBuffer: 4,
    updateWhenIdle: false,
    updateWhenZooming: true,
    attribution: '© Mapbox',
}).addTo(map);


map.on('move', () => {
    const c = map.getCenter();
    document.getElementById('lng-val').textContent = c.lng.toFixed(4);
    document.getElementById('lat-val').textContent = c.lat.toFixed(4);
    document.getElementById('zoom-val').textContent = map.getZoom().toFixed(1);
});

map.on('zoomend', () => {
    const zoom = Math.floor(map.getZoom());
    zoomControl(map, zoom);
});

zoomControl(map, Math.floor(map.getZoom()))
styleSwitcher(map, tileLayer, STYLES)
setUpTripDataBanner()
hideLoading()    
renderTripCoordinates(map)
