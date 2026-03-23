
const requestTripData=async(token)=>{
    const respond = await fetch(TRIP_DATA_URL(token),{
        method:'GET',
        headers:{'Content-Type':'application/json'},
       
    })
    const trip_data =await respond.json()
    return trip_data 
}
const populateBanner=(tripData)=> {
    const trip_name = tripData.trip_name
    const author = tripData.display_name
  document.getElementById('banner-title').textContent      = trip_name        || 'Unnamed Trip';
  document.getElementById('trip-author').textContent      = author        || 'Unknown';
  document.getElementById('banner-author').textContent      = author        || 'Unknown';

  document.getElementById('banner-dates').textContent      = formatDates(tripData.created_time, tripData.ended_time);
}

const formatDates=(start, end)=> {
  if (!start) return '—';
  const fmt = (d) => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  return end ? `${fmt(start)} → ${fmt(end)}` : fmt(start);
}

const setUpTripDataBanner = async () => {
  const TOKEN = window.location.pathname.split('/').pop();
  const res   = await requestTripData(TOKEN);
  console.log(res)
  if (res?.trip_data) populateBanner(res.trip_data);
}
