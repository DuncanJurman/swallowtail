interface ApiConfig {
  baseURL: string
  headers?: Record<string, string>
}

interface ApiError {
  message: string
  status?: number
  errors?: Record<string, string[]>
}

class ApiClient {
  private baseURL: string
  private headers: Record<string, string>

  constructor(config: ApiConfig) {
    this.baseURL = config.baseURL
    this.headers = {
      'Content-Type': 'application/json',
      ...config.headers,
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }))
      throw {
        message: error.message || `Error: ${response.statusText}`,
        status: response.status,
        errors: error.errors,
      } as ApiError
    }

    // Handle empty responses
    if (response.status === 204) {
      return {} as T
    }

    return response.json()
  }

  private getFullURL(endpoint: string): string {
    return `${this.baseURL}${endpoint}`
  }

  async get<T = unknown>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    const url = new URL(this.getFullURL(endpoint))
    if (params) {
      Object.keys(params).forEach((key) => url.searchParams.append(key, String(params[key])))
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.headers,
    })

    return this.handleResponse<T>(response)
  }

  async post<T = unknown>(endpoint: string, body?: unknown): Promise<T> {
    const response = await fetch(this.getFullURL(endpoint), {
      method: 'POST',
      headers: this.headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  async put<T = unknown>(endpoint: string, body?: unknown): Promise<T> {
    const response = await fetch(this.getFullURL(endpoint), {
      method: 'PUT',
      headers: this.headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  async patch<T = unknown>(endpoint: string, body?: unknown): Promise<T> {
    const response = await fetch(this.getFullURL(endpoint), {
      method: 'PATCH',
      headers: this.headers,
      body: body ? JSON.stringify(body) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  async delete<T = unknown>(endpoint: string): Promise<T> {
    const response = await fetch(this.getFullURL(endpoint), {
      method: 'DELETE',
      headers: this.headers,
    })

    return this.handleResponse<T>(response)
  }

  setAuthToken(token: string) {
    this.headers.Authorization = `Bearer ${token}`
  }

  removeAuthToken() {
    delete this.headers.Authorization
  }
}

// Create a singleton instance
const apiClient = new ApiClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
})

export { apiClient, type ApiError }