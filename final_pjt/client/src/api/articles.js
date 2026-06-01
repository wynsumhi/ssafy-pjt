import axios from './axios'

export const getArticleDetail = (id) => {
  return axios.get(`/articles/${id}/`)
}