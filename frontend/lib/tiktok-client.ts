import { apiClient } from './api-client'
import type {
  TikTokAuthRequest,
  TikTokAuthResponse,
  TikTokAccount,
  TikTokPostRequest,
  TikTokPostResponse,
  TikTokCredentials
} from '../types/tiktok'

class TikTokApiClient {
  private basePath = '/tiktok'

  async generateAuthUrl(instanceId: string, accountName?: string): Promise<TikTokAuthResponse> {
    const request: TikTokAuthRequest = {
      instance_id: instanceId,
      account_name: accountName
    }
    
    return apiClient.post<TikTokAuthResponse>(`${this.basePath}/auth`, request)
  }

  async getAccounts(instanceId: string): Promise<TikTokAccount[]> {
    const accounts = await apiClient.get<TikTokCredentials[]>(`${this.basePath}/accounts/${instanceId}`)
    
    // Enhance with computed properties
    return accounts.map(account => {
      const now = new Date()
      const expiresAt = new Date(account.access_token_expires_at)
      const daysUntilExpiry = Math.floor((expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
      
      return {
        ...account,
        is_token_expired: now > expiresAt,
        is_token_expiring_soon: daysUntilExpiry <= 7 && daysUntilExpiry > 0,
        days_until_expiry: daysUntilExpiry
      }
    })
  }

  async disconnectAccount(instanceId: string, accountId: string): Promise<{ status: string; message: string }> {
    return apiClient.delete(`${this.basePath}/disconnect/${instanceId}/${accountId}`)
  }

  async postContent(data: TikTokPostRequest): Promise<TikTokPostResponse> {
    return apiClient.post<TikTokPostResponse>(`${this.basePath}/post`, data)
  }
}

export const tiktokClient = new TikTokApiClient()