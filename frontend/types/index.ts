// Product-related types
export interface ProductIdea {
  name: string
  description: string
  category: string
  target_audience: string
  key_benefits: string[]
  search_volume_trend?: string
  competition_level?: string
  estimated_demand?: string
  rationale: string
  data_sources: string[]
  created_at: string
}

export interface SupplierInfo {
  supplier_name: string
  supplier_url?: string
  unit_cost: number
  minimum_order_quantity: number
  shipping_cost: number
  lead_time_days: number
  supplier_rating?: number
  payment_terms?: string
  notes?: string
}

export interface ProductListing {
  title: string
  description: string
  features: string[]
  specifications: Record<string, string>
  cost: number
  retail_price: number
  sale_price?: number
  images: string[]
  videos: string[]
  meta_title?: string
  meta_description?: string
  keywords: string[]
  status: string
  created_at: string
  updated_at: string
}

// Checkpoint types
export enum CheckpointType {
  PRODUCT_SELECTION = "product_selection",
  SUPPLIER_APPROVAL = "supplier_approval",
  CONTENT_REVIEW = "content_review",
  MARKETING_APPROVAL = "marketing_approval",
  CUSTOM = "custom"
}

export enum CheckpointStatus {
  PENDING = "pending",
  APPROVED = "approved",
  REJECTED = "rejected",
  REVISION_REQUESTED = "revision_requested"
}

export interface HumanCheckpoint {
  id: string
  type: CheckpointType
  title: string
  description: string
  data: Record<string, any>
  status: CheckpointStatus
  created_at: string
  resolved_at?: string
  resolved_by?: string
  resolution_notes?: string
}

// Workflow types
export enum WorkflowStatus {
  IDLE = "idle",
  RESEARCHING = "researching",
  AWAITING_PRODUCT_APPROVAL = "awaiting_product_approval",
  SOURCING = "sourcing",
  AWAITING_SUPPLIER_APPROVAL = "awaiting_supplier_approval",
  CREATING_CONTENT = "creating_content",
  AWAITING_CONTENT_APPROVAL = "awaiting_content_approval",
  PREPARING_MARKETING = "preparing_marketing",
  AWAITING_MARKETING_APPROVAL = "awaiting_marketing_approval",
  LAUNCHING = "launching",
  LIVE = "live",
  ERROR = "error"
}

// API Response types
export interface AgentResult {
  success: boolean
  data?: Record<string, any>
  error?: string
  metadata?: Record<string, any>
}

export interface WorkflowResponse {
  success: boolean
  data?: Record<string, any>
  error?: string
}

export interface CheckpointResolution {
  approved: boolean
  notes?: string
  data?: Record<string, any>
}