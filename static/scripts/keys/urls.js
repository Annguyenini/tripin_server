// const BASE_URL ='http://192.168.0.111:8000'
const BASE_URL ='https://tripping.live'

const TRIP_DATA_URL =(token)=>{
    return `${BASE_URL}/trip/trip-by-token/${token}`
}
const TRIP_COORDINATES_URL=(token)=>{
    return `${BASE_URL}/trip-contents/${token}/coordinates-by-token`
}
const TRIP_MEDIAS_URL=(token)=>{
    return `${BASE_URL}/trip-contents/${token}/medias-by-token`
}