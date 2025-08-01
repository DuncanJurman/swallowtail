export interface TikTokAuthRequest {
  instance_id: string
  scopes?: string[]
  account_name?: string
}

export interface TikTokAuthResponse {
  auth_url: string
  state: string
}

export interface TikTokUserInfo {
  open_id: string
  union_id?: string
  avatar_url?: string
  avatar_url_100?: string
  avatar_large_url?: string
  display_name: string
  bio_description?: string
  profile_deep_link?: string
  is_verified: boolean
  follower_count?: number
  following_count?: number
  likes_count?: number
  video_count?: number
}

export interface TikTokCredentials {
  id: string
  instance_id: string
  tiktok_open_id: string
  tiktok_union_id?: string
  display_name: string
  avatar_url?: string
  account_name?: string
  is_active: 'active' | 'expired' | 'disconnected'
  access_token_expires_at: string
  refresh_token_expires_at: string
  scopes: string[]
  user_info?: TikTokUserInfo
  created_at: string
  updated_at: string
}

export interface TikTokCallbackError {
  error: string
  error_description?: string
}

export interface TikTokCallbackSuccess {
  status: 'success'
  message: string
  user: {
    display_name: string
    open_id: string
  }
}

export interface TikTokPostRequest {
  instance_id: string
  account_id?: string
  video_url?: string
  title: string
  privacy_level?: 'PUBLIC_TO_EVERYONE' | 'MUTUAL_FOLLOW_FRIENDS' | 'SELF_ONLY'
  disable_duet?: boolean
  disable_comment?: boolean
  disable_stitch?: boolean
  video_cover_timestamp_ms?: number
}

export interface TikTokPostResponse {
  post_id?: string
  share_url?: string
  status: 'published' | 'processing' | 'failed'
  error_message?: string
}

export interface TikTokAccount extends TikTokCredentials {
  is_token_expired: boolean
  is_token_expiring_soon: boolean
  days_until_expiry: number
}