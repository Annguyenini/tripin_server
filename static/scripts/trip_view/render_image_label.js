const requestTripMedias =async()=>{
    const response = await fetch (TRIP_MEDIAS_URL(TOKEN),{
        method:'GET',
    })
    const medias = await response.json()
    return medias.medias
}
let _cluster = null
let _zoom = null
let _medias = null
let _clusterMode = true
let _preMeidaArray = null
const renderTripMedias= async (map,zoom) => {
    if (zoom === _zoom) return
    _zoom =zoom
    if (!_medias){
        _medias = await requestTripMedias()
        console.log('setup')
        setUpPolaroidLine(_medias)
        
    }
    
    if (!_cluster ){
        // console.log('compute')
        _cluster = clustersMap(_medias)
    }
    renderImageLabels(_cluster[zoom]||[],map)
}   
const toggleFullMediasMode=()=>{
    _clusterMode = !_clusterMode
    const btn = document.getElementById('cluster-btn')
    btn.textContent = _clusterMode ? 'CLUSTER' : 'ALLMEDIAS'
    btn.classList.toggle('active', !_clusterMode)
    console.log(_clusterMode)
    if(!_clusterMode){
        openPolaroidViewer(_medias||[],0)
    }
    else{
        if(!_preMeidaArray)return
        openPolaroidViewer(_preMeidaArray,0)

    }

}
const clustersMap = (assetsArray) => {
    return {
        10: computeCluster(assetsArray, 1000),
        13: computeCluster(assetsArray, 550),
        15: computeCluster(assetsArray, 250),
        20: computeCluster(assetsArray, 3),
        21: computeCluster(assetsArray, 1),
        22: computeCluster(assetsArray, 0.5)
    }
}

let _markers = []
let _lastMedias =[]
const renderImageLabels = (medias, map) => {
    if (!medias) return;
    if(medias ===_lastMedias) return
    _lastMedias = medias
    // remove old markers
    _markers.forEach(m => m.remove())
    _markers = []

    medias.forEach((media, index) => {
        const el = document.createElement('div');
        el.className = 'img-marker';
        el.innerHTML = `
            ${media.members[0].media_type === 'video'
                ? `<video src="${media.members[0].media_path}" style="width:100%; height:100%; object-fit:cover" muted preload="metadata"></video>
                <div class="img-marker-play"></div>` 
                : `<img src="${media.members[0].media_path}" alt="trip photo" />`
            }
            ${media.members.length > 1
                ? `<div class="img-marker-badge">${media.members.length}</div>`
                : ''}
        `;
        el.id = index

        const marker = new mapboxgl.Marker(el)
            .setLngLat([media.center.lng, media.center.lat])
            .addTo(map);

        // store marker so we can remove it later
        _markers.push(marker)

        el.addEventListener('click', () => {
            _preMeidaArray = media.members
            openPolaroidViewer(media.members, 0)
        })
    });
};
