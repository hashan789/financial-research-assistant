import axios from 'axios'

const axiosInstance = axios.create({
    baseURL: 'https://hashsports-backend-bjdrg6deefc8fhcr.canadacentral-01.azurewebsites.net/api/'
})

export default axiosInstance;