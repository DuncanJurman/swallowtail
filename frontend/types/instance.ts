export enum InstanceType {
  ECOMMERCE = 'ECOMMERCE',
  SOCIAL_MEDIA = 'SOCIAL_MEDIA',
}

export interface Instance {
  id: string
  name: string
  description: string
  type: InstanceType
  business_profile: {
    mission?: string
    target_audience?: string
    brand_voice?: string
    values?: string[]
    goals?: string[]
  }
  visual_identity: {
    primary_color?: string
    secondary_color?: string
    logo_url?: string
    brand_images?: string[]
  }
  platform_connections: Record<string, any>
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface CreateInstanceRequest {
  name: string
  description: string
  type: InstanceType
  business_profile?: Instance['business_profile']
  visual_identity?: Instance['visual_identity']
}