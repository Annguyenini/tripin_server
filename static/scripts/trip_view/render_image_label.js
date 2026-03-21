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
        7 :computeCluster(assetsArray,2500),
        8 :computeCluster(assetsArray,2000),
        9 :computeCluster(assetsArray,1500),
        10 :computeCluster(assetsArray,700),
        11 :computeCluster(assetsArray,400),
        12 :computeCluster(assetsArray,200),
        13 :computeCluster(assetsArray,150),
        14 : computeCluster(assetsArray,50),
        15 : computeCluster(assetsArray,10),
        20 : computeCluster(assetsArray,3),
        21 : computeCluster(assetsArray,2),
        22 : computeCluster(assetsArray,0.5),
    }
}

let _markers = []
let _lastMedias =[]
const renderImageLabels = (medias, map) => {
    if (!medias) return;
    if (medias === _lastMedias) return;
    _lastMedias = medias;

    _markers.forEach(m => m.remove());
    _markers = [];

    medias.forEach((media, index) => {
        const el = document.createElement('div');
        el.className = 'img-marker';
        el.style.cssText = 'width:60px;height:60px;flex-shrink:0;position:relative;';

        const isVideo = media.members[0].media_type === 'video';
        const hasBadge = media.members.length > 1;

        el.innerHTML = `
            ${isVideo
                ? `<video src="${media.members[0].media_path}" style="width:100%;height:100%;object-fit:cover;" muted preload="metadata"></video>
                   <div class="img-marker-play"></div>`
                : `<img src="${media.members[0].media_path}" alt="trip photo" />`
            }
            ${hasBadge ? `<div class="img-marker-badge">${media.members.length}</div>` : ''}
        `;
        el.id = index;

        el.addEventListener('click', () => {
            _preMeidaArray = media.members;
            openPolaroidViewer(media.members, 0);
        });

        const addMarker = () => {
            const marker = new mapboxgl.Marker(el, { anchor: 'center' })
                .setLngLat([media.center.lng, media.center.lat])
                .addTo(map);
            _markers.push(marker);
        };

        if (isVideo) {
            addMarker();
        } else {
            const img = el.querySelector('img');
            img.onload  = addMarker;
            img.onerror = addMarker;
        }
    });
};