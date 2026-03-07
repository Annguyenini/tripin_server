import { TRIP_DATA_URL } from "../keys/urls"

const requestTripData=async(token)=>{
    const respond = await fetch(TRIP_DATA_URL(token),{
        method:'GET',
        headers:{'Content-Type':'application/json'},
       
    })
    const trip_data =await respond.json()
    return trip_data 
}