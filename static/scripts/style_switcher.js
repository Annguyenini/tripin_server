let _currentTileLayer = null;

const styleSwitcher = (map) => {
    const STYLES = {
        streets:   `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
        dark:      `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
        satellite: `https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token=${MAPBOX_TOKEN}`,
    };

    const TILE_OPTIONS = {
        tileSize: 512,
        zoomOffset: -1,
        detectRetina: true,
        maxZoom: 22,
        maxNativeZoom: 18,
        keepBuffer: 4,
        updateWhenIdle: false,
        updateWhenZooming: true,
        attribution: '© Mapbox',
    };

    const switchStyle = (key) => {
        const newLayer = L.tileLayer(STYLES[key], TILE_OPTIONS).addTo(map);
        if (_currentTileLayer) _currentTileLayer.remove();
        _currentTileLayer = newLayer;

        document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(`style-${key}`).classList.add('active');
    };

    const styleBtns = { dark: 'style-dark', streets: 'style-streets', satellite: 'style-satellite' };
    Object.entries(styleBtns).forEach(([key, btnId]) => {
        document.getElementById(btnId).onclick = () => switchStyle(key);
    });

    // init with streets
    switchStyle('streets');
};