// show/hide functions
const showLoading = (text = 'loading your trip...') => {
  const overlay = document.getElementById('loading-overlay')
  overlay.querySelector('.loading-text').textContent = text
  overlay.classList.remove('hidden')
}

const hideLoading = () => {
  document.getElementById('loading-overlay').classList.add('hidden')
}

// use it around your data fetching
const init = async () => {
  showLoading('loading your trip...')
  
  await requestTripData(TOKEN)
  await renderTripCoordinates(map)
  await renderTripMedias(map, map.getZoom())

  hideLoading()
}