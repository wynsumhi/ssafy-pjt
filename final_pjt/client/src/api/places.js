import axios from './axios'

export const getPlaceDetail = (cid) => {
  return axios.get(`/places/${cid}/`)
}
