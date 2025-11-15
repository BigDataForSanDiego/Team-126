import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const authStorage = localStorage.getItem('auth-storage')
    if (authStorage) {
      try {
        const { state } = JSON.parse(authStorage)
        if (state.token) {
          config.headers.Authorization = `Bearer ${state.token}`
          console.log('[Auth] Token attached:', state.token.substring(0, 20) + '...')
        } else {
          console.warn('[Auth] No token found in state')
        }
      } catch (error) {
        console.error('[Auth] Error parsing auth storage:', error)
      }
    } else {
      console.warn('[Auth] No auth-storage found in localStorage')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('[Auth] 401 Unauthorized - Token may be invalid or expired')
      // You could add logic here to redirect to login page
    }
    return Promise.reject(error)
  }
)

// API functions
export const api = {
  // Auth
  register: async (data: { username?: string; email?: string; password?: string; is_guest?: boolean }) => {
    const response = await apiClient.post('/register', data)
    return response.data
  },

  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await apiClient.post('/token', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  loginFace: async (imageFile: File) => {
    const formData = new FormData()
    formData.append('file', imageFile)
    const response = await apiClient.post('/login/face', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  registerFace: async (imageFile: File) => {
    const formData = new FormData()
    formData.append('file', imageFile)
    const response = await apiClient.post('/register/face', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  // User
  getMe: async () => {
    const response = await apiClient.get('/me')
    return response.data
  },

  selectCharacter: async (character_id: number, user_id: number) => {
    const response = await apiClient.post('/character/select', { character_id, user_id })
    return response.data
  },

  // Conversation
  startConversation: async (user_id: number) => {
    const response = await apiClient.post('/conversation/start', { user_id })
    return response.data
  },

  endConversation: async (conversation_id: number) => {
    const response = await apiClient.post(`/conversation/${conversation_id}/end`)
    return response.data
  },

  getReport: async (conversation_id: number) => {
    const response = await apiClient.get(`/conversation/${conversation_id}/report`)
    return response.data
  },
}

export { API_BASE_URL }
