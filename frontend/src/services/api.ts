import axios, { AxiosInstance, AxiosResponse } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // 請求攔截器
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // 回應攔截器
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('API Response Error:', error)
        // 這裡可以添加全局錯誤處理
        return Promise.reject(error)
      }
    )
  }

  // GET 請求
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.api.get<T>(url, { params })
    return response.data
  }

  // POST 請求
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.post<T>(url, data)
    return response.data
  }

  // PUT 請求
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.put<T>(url, data)
    return response.data
  }

  // DELETE 請求
  async delete<T>(url: string): Promise<T> {
    const response = await this.api.delete<T>(url)
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService