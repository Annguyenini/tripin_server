const allowedZooms = [7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 21, 22];
let _zoomRef = null;

const zoomControl = (map, zoom) => {
  console.log("zoome call", _zoomRef);
  if (zoom === _zoomRef) return;
  if (!allowedZooms.includes(zoom)) return;
  _zoomRef = zoom;
  renderMarkers(map, zoom);
};
