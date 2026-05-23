const renderTripCoordinates = async (content_cards, map) => {
  map.flyTo([content_cards[0].latitude, content_cards[0].longitude], 18, {
    duration: 3.5,
    easeLinearity: 0, // closer to 0 = more ease in/out, smoother
    animate: true,
  });
  // draw line
  content_cards = content_cards.filter((c) => c.event !== "remove");

  const latlngs = content_cards.map((c) => [c.latitude, c.longitude]);
  L.polyline(latlngs, {
    color: "#1a1a1a",
    weight: 2,
    dashArray: "6, 6",
  }).addTo(map);

  // draw dots
  content_cards.forEach((c) => {
    L.circleMarker([c.latitude, c.longitude], {
      radius: 6,
      color: "#f0f0ec",
      fillColor: "#1a1a1a",
      fillOpacity: 1,
      weight: 2,
    }).addTo(map);
  });

  // trigger first media render
  const zoom = Math.floor(map.getZoom());
  // renderTripMedias(map, zoom);
  hideLoading();
};
