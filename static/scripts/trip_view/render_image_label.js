const requestTripContents = async () => {
  const response = await fetch(TRIP_CONTENTS_URL(TOKEN), {
    method: "GET",
  });
  const medias = await response.json();
  return medias?.content_cards;
};
let _cluster = null;
let _zoom = null;
let _content_card = null;
let _clusterMode = true;
let _preMeidaArray = null;
let _fresh_start = true;
const renderMarkers = async (map, zoom) => {
  if (zoom === _zoom) return;
  _zoom = zoom;
  if (!_content_card) {
    _content_card = await requestTripContents();

    // setUpPolaroidLine(_content_card)
  }

  if (!_cluster) {
    // console.log('compute')
    _content_card = _content_card.filter((m) => m.event !== "remove");
    _cluster = clustersMap(_content_card);
  }
  renderImageLabels(_cluster[zoom] || [], map);
  if (_fresh_start) {
    renderTripCoordinates(_content_card, map);
    _fresh_start = false;
  }
};
const toggleFullMediasMode = () => {
  _clusterMode = !_clusterMode;
  const btn = document.getElementById("cluster-btn");
  btn.textContent = _clusterMode ? "CLUSTER" : "ALLMEDIAS";
  btn.classList.toggle("active", !_clusterMode);
  // console.log(_clusterMode);
  if (!_clusterMode) {
    openPolaroidViewer(_content_card || [], 0);
  } else {
    if (!_preMeidaArray) return;
    openPolaroidViewer(_preMeidaArray, 0);
  }
};
const clustersMap = (assetsArray) => {
  return {
    7: computeCluster(assetsArray, 2500),
    8: computeCluster(assetsArray, 2000),
    9: computeCluster(assetsArray, 1500),
    10: computeCluster(assetsArray, 700),
    11: computeCluster(assetsArray, 400),
    12: computeCluster(assetsArray, 200),
    13: computeCluster(assetsArray, 150),
    14: computeCluster(assetsArray, 50),
    15: computeCluster(assetsArray, 10),
    16: computeCluster(assetsArray, 9),
    17: computeCluster(assetsArray, 7),
    18: computeCluster(assetsArray, 5),
    19: computeCluster(assetsArray, 4),
    20: computeCluster(assetsArray, 3),
    21: computeCluster(assetsArray, 2),
    22: computeCluster(assetsArray, 0.5),
  };
};

let _markers = [];
let _lastMedias = [];

const renderImageLabels = (medias, map) => {
  if (!medias) return;
  if (medias === _lastMedias) return;
  _lastMedias = medias;

  _markers.forEach((m) => m.remove());
  _markers = [];
  // console.log(medias);

  medias.forEach((media) => {
    // console.log(media);
    if (media.event === "remove") return;
    const el = document.createElement("div");
    el.className = "img-marker";
    el.style.cssText = "width:60px;height:60px;position:relative;";

    const isVideo = media.members[0].media_type === "video";
    const hasBadge = media.members.length > 1;

    el.innerHTML = `
            ${
              isVideo
                ? `<video src="${media.members[0].media_path}" style="width:100%;height:100%;object-fit:cover;" muted preload="metadata"></video>
                   <div class="img-marker-play"></div>`
                : `<img src="${media.members[0].media_path}" alt="trip photo" style="width:100%;height:100%;object-fit:cover;display:block;"/>`
            }
            ${hasBadge ? `<div class="img-marker-badge">${media.members.length}</div>` : ""}
        `;

    el.addEventListener("click", () => {
      _preMeidaArray = media.members;
      openPolaroidViewer(media.members, 0);
    });

    const icon = L.divIcon({
      html: el,
      className: "",
      iconSize: [60, 60],
      iconAnchor: [30, 30], // perfect center
    });

    const marker = L.marker([media.center.lat, media.center.lng], {
      icon,
    }).addTo(map);
    _markers.push(marker);
  });
};
