# Product Lifecycle Implementation Plan

## Executive Summary

This document outlines the implementation strategy for the Product Lifecycle Management system in Swallowtail. Each approved product instance will have its own set of specialized AI agents handling different aspects of the product's journey from launch to maturity. The system is designed to be highly customizable, allowing users to edit agent prompts and behaviors through the frontend interface.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Product Instance Management](#product-instance-management)
3. [Agent Specifications](#agent-specifications)
4. [Tool Integrations](#tool-integrations)
5. [Inter-Agent Communication Protocol](#inter-agent-communication-protocol)
6. [Customization Framework](#customization-framework)
7. [Database Schema](#database-schema)
8. [Implementation Roadmap](#implementation-roadmap)

---

## System Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Product Instance Alpha                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Product Orchestrator                      │  │
│  │  • Lifecycle Management                              │  │
│  │  • Agent Coordination                                │  │
│  │  • State Management                                  │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────┼────────────────────────────────┐  │
│  │                    ▼                                 │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│  │
│  │  │ Image   │  │ Video   │  │  Ad     │  │Fulfill- ││  │
│  │  │   Gen   │  │  Gen    │  │ Agent   │  │  ment   ││  │
│  │  │  Agent  │  │ Agent   │  │         │  │  Agent  ││  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘│  │
│  │                                                      │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│  │
│  │  │Analytics│  │Customer │  │ Content │  │ Pricing ││  │
│  │  │  Agent  │  │ Service │  │  Agent  │  │  Agent  ││  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘│  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  State: Redis Namespace "product:alpha:*"                  │
│  Config: Custom per-product settings                       │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Product Isolation**: Each product instance operates independently with its own state and configuration
2. **Agent Modularity**: Agents can be enabled/disabled per product based on needs
3. **Customizability**: All agent behaviors can be customized through configuration
4. **Shared Learning**: While isolated, products contribute to shared knowledge base
5. **Progressive Automation**: Automation level increases as product matures

---

## Product Instance Management

### Product Instance Class

```python
class ProductInstance:
    """Manages a single product's lifecycle and agents."""
    
    def __init__(self, product_id: str, opportunity_data: MarketOpportunity, config: ProductConfig):
        self.product_id = product_id
        self.opportunity_data = opportunity_data
        self.config = config
        
        # Initialize components
        self.orchestrator = ProductOrchestrator(product_id)
        self.state_manager = ProductStateManager(f"product:{product_id}")
        self.agents = self._initialize_agents()
        self.lifecycle_stage = LifecycleStage.DISCOVERY
        
    def _initialize_agents(self) -> Dict[str, BaseProductAgent]:
        """Initialize all agents for this product instance."""
        agents = {}
        
        # Core agents - always enabled
        agents['content'] = ContentGenerationAgent(self.product_id, self.config.content_config)
        agents['image'] = ImageGenerationAgent(self.product_id, self.config.image_config)
        agents['fulfillment'] = FulfillmentAgent(self.product_id, self.config.fulfillment_config)
        
        # Optional agents - based on configuration
        if self.config.enable_video:
            agents['video'] = VideoGenerationAgent(self.product_id, self.config.video_config)
            
        if self.config.enable_advertising:
            agents['advertising'] = AdvertisementAgent(self.product_id, self.config.ad_config)
            
        if self.config.enable_analytics:
            agents['analytics'] = AnalyticsAgent(self.product_id, self.config.analytics_config)
            
        return agents
```

### Lifecycle Stages

```python
class LifecycleStage(Enum):
    DISCOVERY = "discovery"          # Initial research and setup
    LAUNCH_PREP = "launch_prep"      # Content creation and preparation
    LAUNCH = "launch"                # Going live
    GROWTH = "growth"                # Scaling and optimization
    MATURITY = "maturity"            # Steady state operations
    DECLINE = "decline"              # End of life management

class StageConfig:
    """Configuration for each lifecycle stage."""
    
    STAGE_SETTINGS = {
        LifecycleStage.DISCOVERY: {
            "automation_level": 0.2,
            "human_checkpoints": ["supplier_selection", "initial_content", "pricing_strategy"],
            "active_agents": ["content", "image", "fulfillment"],
            "budget_limit_daily": 0  # No spending yet
        },
        LifecycleStage.LAUNCH_PREP: {
            "automation_level": 0.4,
            "human_checkpoints": ["final_content_review", "campaign_approval"],
            "active_agents": ["content", "image", "video", "advertising"],
            "budget_limit_daily": 50
        },
        LifecycleStage.LAUNCH: {
            "automation_level": 0.6,
            "human_checkpoints": ["go_live_approval"],
            "active_agents": ["all"],
            "budget_limit_daily": 100
        },
        LifecycleStage.GROWTH: {
            "automation_level": 0.8,
            "human_checkpoints": ["major_strategy_changes"],
            "active_agents": ["all"],
            "budget_limit_daily": 500
        },
        LifecycleStage.MATURITY: {
            "automation_level": 0.95,
            "human_checkpoints": ["exception_handling"],
            "active_agents": ["all"],
            "budget_limit_daily": 1000
        }
    }
```

---

## Agent Specifications

### 1. Image/Infographic Generation Agent

#### Purpose
Generate all visual content for the product including main product images, lifestyle shots, infographics, and marketing materials.

#### Core Capabilities
- Product photography generation (multiple angles, backgrounds)
- Lifestyle photography with target demographic
- Infographic creation for features/benefits
- Size charts and comparison graphics
- Social media content adaptation
- A/B testing different visual styles

#### Tool Integrations
```yaml
primary_tools:
  image_generation:
    # PRIMARY IMPLEMENTATION - To be implemented first
    - service: "OpenAI gpt-image-1"
      use_cases: ["product_shots", "lifestyle_images", "all_image_generation"]
      api_endpoint: "https://api.openai.com/v1/images/generations"
      models:
        - "dall-e-3"  # High quality, detailed images
        - "dall-e-2"  # Faster, more variations
      capabilities:
        - text_to_image: true
        - image_variations: true  # dall-e-2 only
        - sizes: ["1024x1024", "1792x1024", "1024x1792"]  # dall-e-3
        - quality: ["standard", "hd"]  # dall-e-3 only
        - style: ["vivid", "natural"]  # dall-e-3 only
      priority: "HIGH - IMPLEMENT FIRST"
      
    # FUTURE IMPLEMENTATIONS
    - service: "Stable Diffusion API"
      use_cases: ["bulk_variations", "background_removal"]
      endpoint: "https://api.stability.ai"
      priority: "MEDIUM - Phase 2"
      
    - service: "Midjourney API"
      use_cases: ["artistic_renders", "brand_imagery"]
      priority: "LOW - Phase 3"
      
  image_editing:
    - service: "Remove.bg"
      use_cases: ["background_removal"]
      
    - service: "Canva API"
      use_cases: ["templates", "infographics", "social_media"]
      
  optimization:
    - service: "TinyPNG API"
      use_cases: ["compression", "format_conversion"]
```

#### Agent Configuration Schema
```python
class ImageAgentConfig(BaseModel):
    """Configuration for Image Generation Agent."""
    
    # Style settings
    visual_style: str = Field(..., description="minimalist|lifestyle|luxury|technical|playful")
    color_palette: List[str] = Field(..., description="Hex codes for brand colors")
    
    # Image requirements
    product_shots: Dict[str, Any] = {
        "main_image": {
            "background": "white",
            "angle": "front_facing",
            "lighting": "studio"
        },
        "gallery_images": {
            "count": 5,
            "angles": ["front", "back", "side", "detail", "in_use"],
            "backgrounds": ["white", "lifestyle", "gradient"]
        }
    }
    
    lifestyle_settings: Dict[str, Any] = {
        "environments": ["home", "outdoor", "office"],
        "model_demographics": {
            "age_range": [25, 45],
            "diversity": True
        },
        "props": ["relevant_to_product"]
    }
    
    infographic_templates: List[str] = ["features", "size_chart", "comparison", "how_to_use"]
    
    # Quality settings
    output_formats: List[str] = ["webp", "jpg", "png"]
    compression_level: float = 0.85
    
    # Customizable prompts
    prompts: Dict[str, str] = {
        "main_product": "Professional product photography of {product_name}, white background, studio lighting, high detail, commercial quality",
        "lifestyle": "Person using {product_name} in {environment}, natural lighting, authentic feel, {brand_style} aesthetic",
        "infographic": "Clean infographic showing {content_type} for {product_name}, {color_palette} color scheme, modern design"
    }
```

#### Implementation Example
```python
class ImageGenerationAgent(BaseProductAgent):
    """Agent responsible for all visual content generation."""
    
    def __init__(self, product_id: str, config: ImageAgentConfig):
        super().__init__(product_id, "image_generation")
        self.config = config
        # PRIMARY: OpenAI gpt-image-1 client
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # FUTURE: Other clients to be added in phases
        # self.stability_client = StabilityClient()  # Phase 2
        self.canva_client = CanvaAPI()  # For templates/editing
        
    async def generate_product_images(self, product_data: ProductData) -> ImageSet:
        """Generate complete set of product images."""
        images = ImageSet()
        
        # Generate main product shot
        main_prompt = self._customize_prompt(
            self.config.prompts["main_product"],
            product_name=product_data.name
        )
        
        # Using gpt-image-1 API (DALL-E 3 model)
        response = await self.openai_client.images.generate(
            model="dall-e-3",  # gpt-image-1 supports both dall-e-2 and dall-e-3
            prompt=main_prompt,
            n=1,  # Number of images
            size="1024x1024",  # dall-e-3 supports: 1024x1024, 1792x1024, 1024x1792
            quality="hd",  # 'standard' or 'hd' - unique to dall-e-3
            style="natural",  # 'vivid' or 'natural' - unique to dall-e-3
            response_format="url"  # or 'b64_json' for base64 encoded
        )
        
        main_image = response.data[0]
        
        # Process and optimize
        processed = await self._process_image(main_image, "main")
        images.main_image = processed
        
        # Generate gallery images
        for angle in self.config.product_shots["gallery_images"]["angles"]:
            angle_image = await self._generate_angle_shot(product_data, angle)
            images.gallery.append(angle_image)
            
        # Generate lifestyle images
        for env in self.config.lifestyle_settings["environments"]:
            lifestyle_image = await self._generate_lifestyle_shot(product_data, env)
            images.lifestyle.append(lifestyle_image)
            
        return images
        
    async def create_infographic(self, content_type: str, data: Dict) -> Image:
        """Create infographic using templates."""
        template = await self.canva_client.get_template(content_type)
        
        customized = await self.canva_client.customize_template(
            template_id=template.id,
            brand_colors=self.config.color_palette,
            content=data
        )
        
        return await self.canva_client.render(customized)
```

### 2. Video Generation Agent

#### Purpose
Create engaging video content for products including demonstrations, unboxing experiences, and social media content.

#### Core Capabilities
- Product demonstration videos
- Unboxing/reveal videos
- Social media shorts (TikTok, Reels, Shorts)
- Tutorial/how-to videos
- Customer testimonial recreations
- Multi-language voiceover support

#### Tool Integrations
```yaml
video_generation:
  - service: "Google Veo 3"
    capabilities: ["text_to_video", "image_to_video"]
    max_duration: 60
    
  - service: "Runway ML Gen-3"
    capabilities: ["video_editing", "effects", "transitions"]
    
  - service: "D-ID"
    capabilities: ["ai_presenter", "talking_head"]
    
audio_generation:
  - service: "ElevenLabs"
    capabilities: ["voiceover", "multilingual", "voice_cloning"]
    
  - service: "Mubert API"
    capabilities: ["background_music", "custom_tracks"]
    
video_processing:
  - service: "FFmpeg"
    capabilities: ["encoding", "format_conversion", "optimization"]
```

#### Agent Configuration Schema
```python
class VideoAgentConfig(BaseModel):
    """Configuration for Video Generation Agent."""
    
    # Video settings
    video_types: List[str] = ["product_demo", "unboxing", "social_short", "tutorial"]
    default_duration: int = Field(30, description="Default video length in seconds")
    aspect_ratios: Dict[str, str] = {
        "youtube": "16:9",
        "tiktok": "9:16",
        "instagram_reel": "9:16",
        "instagram_post": "1:1"
    }
    
    # Style settings
    visual_style: str = "modern|vintage|minimalist|energetic|luxury"
    transition_style: str = "smooth|dynamic|cut|fade"
    
    # Audio settings
    voiceover_config: Dict[str, Any] = {
        "enabled": True,
        "voice_id": "default",
        "language": "en-US",
        "tone": "friendly|professional|enthusiastic|calm",
        "speed": 1.0
    }
    
    music_config: Dict[str, Any] = {
        "enabled": True,
        "genre": "corporate|upbeat|ambient|electronic",
        "energy_level": "high|medium|low",
        "volume": 0.3
    }
    
    # Content templates
    video_scripts: Dict[str, str] = {
        "product_demo": """
        Scene 1 (0-3s): Product reveal with brand logo
        Scene 2 (3-10s): Key features demonstration
        Scene 3 (10-20s): Product in use
        Scene 4 (20-27s): Benefits highlight
        Scene 5 (27-30s): Call to action with website
        """,
        "unboxing": """
        Scene 1 (0-5s): Package arrival
        Scene 2 (5-15s): Opening sequence
        Scene 3 (15-25s): Product reveal and first impressions
        Scene 4 (25-30s): Final shot with CTA
        """
    }
    
    # Platform-specific settings
    platform_optimizations: Dict[str, Dict] = {
        "tiktok": {
            "max_duration": 60,
            "hook_duration": 3,
            "captions": True,
            "trending_sounds": True
        },
        "youtube_shorts": {
            "max_duration": 60,
            "end_screen": True
        }
    }
```

#### Implementation Example
```python
class VideoGenerationAgent(BaseProductAgent):
    """Agent responsible for video content creation."""
    
    def __init__(self, product_id: str, config: VideoAgentConfig):
        super().__init__(product_id, "video_generation")
        self.config = config
        self.veo_client = GoogleVeoClient()
        self.runway_client = RunwayMLClient()
        self.elevenlabs_client = ElevenLabsClient()
        
    async def create_product_video(self, 
                                  video_type: str, 
                                  product_data: ProductData,
                                  images: ImageSet) -> Video:
        """Create a complete product video."""
        
        # Generate script based on template
        script = self._generate_script(video_type, product_data)
        
        # Generate voiceover if enabled
        voiceover = None
        if self.config.voiceover_config["enabled"]:
            voiceover = await self._generate_voiceover(script)
            
        # Generate video scenes
        scenes = []
        for scene in script.scenes:
            if scene.type == "product_shot":
                # Use existing product images
                scene_video = await self.veo_client.image_to_video(
                    image=images.get_image(scene.image_type),
                    motion=scene.motion_type,
                    duration=scene.duration
                )
            else:
                # Generate new video content
                scene_video = await self.veo_client.text_to_video(
                    prompt=scene.prompt,
                    duration=scene.duration,
                    style=self.config.visual_style
                )
            scenes.append(scene_video)
            
        # Combine scenes with transitions
        combined = await self.runway_client.combine_clips(
            clips=scenes,
            transitions=self.config.transition_style
        )
        
        # Add audio layers
        if voiceover:
            combined = await self._add_audio_track(combined, voiceover, "voiceover")
            
        if self.config.music_config["enabled"]:
            music = await self._generate_background_music(script.total_duration)
            combined = await self._add_audio_track(combined, music, "music")
            
        # Platform-specific optimizations
        final_videos = {}
        for platform in ["youtube", "tiktok", "instagram"]:
            optimized = await self._optimize_for_platform(combined, platform)
            final_videos[platform] = optimized
            
        return VideoSet(videos=final_videos, master=combined)
        
    async def create_social_short(self, 
                                 product_data: ProductData,
                                 trend_data: Optional[TrendData] = None) -> Video:
        """Create trending social media content."""
        
        # Analyze current trends if not provided
        if not trend_data:
            trend_data = await self._analyze_video_trends(product_data.category)
            
        # Generate hook (first 3 seconds are crucial)
        hook_prompt = self._generate_hook_prompt(product_data, trend_data)
        hook = await self.veo_client.text_to_video(
            prompt=hook_prompt,
            duration=3,
            style="attention_grabbing"
        )
        
        # Generate main content
        main_content = await self._generate_trending_content(product_data, trend_data)
        
        # Add trending audio if available
        if trend_data.trending_audio:
            main_content = await self._add_trending_audio(main_content, trend_data.trending_audio)
            
        # Add captions and effects
        final = await self._add_social_elements(main_content, platform="tiktok")
        
        return final
```

### 3. Advertisement Agent

#### Purpose
Manage all paid advertising campaigns across multiple platforms, optimizing for ROI and conversions.

#### Core Capabilities
- Multi-platform campaign management
- Dynamic creative optimization
- Audience targeting and segmentation
- Budget allocation and optimization
- A/B testing automation
- Performance tracking and reporting
- Bid strategy optimization

#### Tool Integrations
```yaml
advertising_platforms:
  - platform: "Facebook/Instagram Ads"
    api: "Meta Marketing API"
    capabilities: ["campaigns", "audiences", "creative", "insights"]
    
  - platform: "Google Ads"
    api: "Google Ads API"
    capabilities: ["search", "shopping", "display", "youtube"]
    
  - platform: "TikTok Ads"
    api: "TikTok Marketing API"
    capabilities: ["in_feed", "top_view", "branded_effects"]
    
  - platform: "Pinterest Ads"
    api: "Pinterest Marketing API"
    capabilities: ["promoted_pins", "shopping_ads"]
    
analytics_tools:
  - service: "Google Analytics 4"
    use_case: "conversion_tracking"
    
  - service: "Meta Pixel"
    use_case: "retargeting"
    
optimization_tools:
  - service: "Internal ML Models"
    capabilities: ["bid_optimization", "audience_prediction", "creative_scoring"]
```

#### Agent Configuration Schema
```python
class AdvertisementAgentConfig(BaseModel):
    """Configuration for Advertisement Agent."""
    
    # Platform settings
    enabled_platforms: List[str] = ["facebook", "instagram", "google", "tiktok"]
    
    # Budget configuration
    budget_config: Dict[str, Any] = {
        "daily_limit": 100.0,
        "monthly_limit": 3000.0,
        "platform_allocation": {
            "facebook": 0.3,
            "instagram": 0.2,
            "google": 0.35,
            "tiktok": 0.15
        },
        "auto_scale": {
            "enabled": True,
            "min_roi": 2.0,
            "scale_factor": 1.5,
            "max_daily": 500.0
        }
    }
    
    # Targeting configuration
    targeting_config: Dict[str, Any] = {
        "demographics": {
            "age_range": [25, 54],
            "genders": ["all"],
            "income_level": "middle_to_high"
        },
        "interests": ["eco-friendly", "sustainability", "outdoor activities"],
        "behaviors": ["online_shopping", "early_technology_adopters"],
        "custom_audiences": {
            "lookalike": True,
            "retargeting": True,
            "email_list": True
        }
    }
    
    # Creative configuration
    creative_config: Dict[str, Any] = {
        "ad_formats": ["single_image", "carousel", "video", "collection"],
        "copy_variations": 5,
        "image_variations": 3,
        "dynamic_creative": True,
        "copy_tone": "friendly|professional|urgent|aspirational"
    }
    
    # Campaign strategies
    campaign_strategies: Dict[str, Dict] = {
        "launch": {
            "objective": "awareness",
            "bid_strategy": "lowest_cost",
            "placements": ["feed", "stories", "reels"]
        },
        "growth": {
            "objective": "conversions",
            "bid_strategy": "target_cpa",
            "target_cpa": 25.0
        },
        "retargeting": {
            "objective": "conversions",
            "audience": "website_visitors_7d",
            "frequency_cap": 3
        }
    }
    
    # Optimization rules
    optimization_rules: List[Dict] = [
        {
            "condition": "ctr < 0.5%",
            "action": "pause_ad",
            "after_impressions": 1000
        },
        {
            "condition": "cpa > target_cpa * 1.5",
            "action": "decrease_bid",
            "amount": 0.1
        },
        {
            "condition": "roas > 3.0",
            "action": "increase_budget",
            "amount": 0.25
        }
    ]
```

#### Implementation Example
```python
class AdvertisementAgent(BaseProductAgent):
    """Agent responsible for all paid advertising activities."""
    
    def __init__(self, product_id: str, config: AdvertisementAgentConfig):
        super().__init__(product_id, "advertisement")
        self.config = config
        self.meta_ads = MetaAdsAPI()
        self.google_ads = GoogleAdsAPI()
        self.tiktok_ads = TikTokAdsAPI()
        
    async def launch_campaign(self, 
                            campaign_type: str,
                            product_data: ProductData,
                            creative_assets: CreativeAssets) -> CampaignResult:
        """Launch a new advertising campaign."""
        
        strategy = self.config.campaign_strategies[campaign_type]
        
        # Generate ad copy variations
        ad_copies = await self._generate_ad_copies(
            product_data,
            count=self.config.creative_config["copy_variations"],
            tone=self.config.creative_config["copy_tone"]
        )
        
        # Create campaigns on each platform
        campaigns = {}
        
        for platform in self.config.enabled_platforms:
            if platform in ["facebook", "instagram"]:
                campaign = await self._create_meta_campaign(
                    platform=platform,
                    strategy=strategy,
                    product_data=product_data,
                    ad_copies=ad_copies,
                    creative_assets=creative_assets
                )
                campaigns[platform] = campaign
                
            elif platform == "google":
                campaign = await self._create_google_campaign(
                    strategy=strategy,
                    product_data=product_data,
                    ad_copies=ad_copies
                )
                campaigns[platform] = campaign
                
            elif platform == "tiktok":
                campaign = await self._create_tiktok_campaign(
                    strategy=strategy,
                    product_data=product_data,
                    creative_assets=creative_assets
                )
                campaigns[platform] = campaign
                
        # Set up tracking
        await self._setup_conversion_tracking(campaigns)
        
        # Initialize optimization monitoring
        await self._start_optimization_monitoring(campaigns)
        
        return CampaignResult(campaigns=campaigns, status="launched")
        
    async def optimize_campaigns(self, performance_data: Dict) -> OptimizationResult:
        """Continuously optimize running campaigns."""
        
        optimizations_made = []
        
        for platform, metrics in performance_data.items():
            # Apply optimization rules
            for rule in self.config.optimization_rules:
                if self._evaluate_condition(rule["condition"], metrics):
                    optimization = await self._apply_optimization(
                        platform=platform,
                        action=rule["action"],
                        params=rule
                    )
                    optimizations_made.append(optimization)
                    
            # ML-based optimizations
            if self.config.budget_config["auto_scale"]["enabled"]:
                if metrics.get("roi", 0) > self.config.budget_config["auto_scale"]["min_roi"]:
                    scale_result = await self._scale_campaign(
                        platform=platform,
                        factor=self.config.budget_config["auto_scale"]["scale_factor"]
                    )
                    optimizations_made.append(scale_result)
                    
        # Rebalance budget across platforms based on performance
        rebalance_result = await self._rebalance_platform_budgets(performance_data)
        if rebalance_result:
            optimizations_made.append(rebalance_result)
            
        return OptimizationResult(optimizations=optimizations_made)
        
    async def _create_meta_campaign(self, **kwargs) -> MetaCampaign:
        """Create Facebook/Instagram campaign."""
        
        # Create campaign
        campaign = await self.meta_ads.create_campaign(
            name=f"{kwargs['product_data'].name} - {kwargs['strategy']['objective']}",
            objective=kwargs['strategy']['objective'],
            budget_daily=self._calculate_platform_budget(kwargs['platform'])
        )
        
        # Create ad sets with targeting
        ad_set = await self.meta_ads.create_ad_set(
            campaign_id=campaign.id,
            targeting=self._build_meta_targeting(),
            placements=kwargs['strategy']['placements'],
            bid_strategy=kwargs['strategy']['bid_strategy']
        )
        
        # Create dynamic creative ads
        for i, copy in enumerate(kwargs['ad_copies']):
            for image in kwargs['creative_assets'].images[:3]:  # Top 3 images
                ad = await self.meta_ads.create_ad(
                    ad_set_id=ad_set.id,
                    creative={
                        "image": image.url,
                        "primary_text": copy.primary_text,
                        "headline": copy.headline,
                        "call_to_action": copy.cta,
                        "link": kwargs['product_data'].landing_page_url
                    }
                )
                
        return campaign
```

### 4. Fulfillment Agent

#### Purpose
Handle all aspects of order fulfillment, inventory management, and supplier coordination.

#### Core Capabilities
- Order processing and tracking
- Inventory level monitoring
- Automated reordering
- Supplier communication
- Shipping coordination
- Returns/refunds processing
- Quality control monitoring

#### Tool Integrations
```yaml
ecommerce_platforms:
  - platform: "Shopify"
    api: "Shopify Admin API"
    capabilities: ["orders", "inventory", "fulfillment", "customers"]
    
  - platform: "WooCommerce"
    api: "WooCommerce REST API"
    capabilities: ["orders", "stock", "shipping"]
    
supplier_integrations:
  - type: "API"
    providers: ["Alibaba", "Printful", "Spocket"]
    
  - type: "Email"
    providers: ["custom_suppliers"]
    automation: "template_based"
    
shipping_providers:
  - carrier: "USPS"
    api: "USPS Web Tools API"
    
  - carrier: "UPS"
    api: "UPS API"
    
  - carrier: "FedEx"
    api: "FedEx Web Services"
    
  - aggregator: "ShipStation"
    api: "ShipStation API"
    
inventory_tools:
  - service: "Internal Forecasting"
    capabilities: ["demand_prediction", "reorder_points"]
```

#### Agent Configuration Schema
```python
class FulfillmentAgentConfig(BaseModel):
    """Configuration for Fulfillment Agent."""
    
    # Platform settings
    ecommerce_platform: str = "shopify"
    store_url: str
    
    # Inventory settings
    inventory_config: Dict[str, Any] = {
        "reorder_point_days": 14,  # Days of inventory to maintain
        "safety_stock_multiplier": 1.5,
        "max_stock_days": 90,
        "low_stock_alert_threshold": 0.2,
        "forecasting_method": "moving_average|ml_based"
    }
    
    # Supplier settings
    supplier_config: Dict[str, Any] = {
        "primary_supplier": {
            "id": "supplier_123",
            "name": "Eco Bottles Inc",
            "type": "api|email",
            "lead_time_days": 21,
            "moq": 500,
            "payment_terms": "net_30"
        },
        "backup_suppliers": [
            {
                "id": "supplier_456",
                "activation_condition": "primary_out_of_stock",
                "price_premium": 0.15
            }
        ],
        "quality_check_rate": 0.05  # Check 5% of orders
    }
    
    # Shipping settings
    shipping_config: Dict[str, Any] = {
        "default_carrier": "usps",
        "shipping_methods": {
            "standard": {
                "carrier": "usps",
                "service": "priority",
                "days": "3-5"
            },
            "express": {
                "carrier": "fedex",
                "service": "2day",
                "days": "2"
            }
        },
        "international": {
            "enabled": True,
            "restricted_countries": ["XX", "YY"]
        },
        "tracking_notification": True
    }
    
    # Order processing
    order_processing: Dict[str, Any] = {
        "auto_fulfill": True,
        "batch_processing": {
            "enabled": True,
            "time": "14:00",  # 2 PM daily
            "min_orders": 10
        },
        "fraud_check": {
            "enabled": True,
            "service": "shopify_fraud_analysis"
        }
    }
    
    # Returns configuration
    returns_config: Dict[str, Any] = {
        "return_window_days": 30,
        "return_reasons": [
            "defective",
            "not_as_described",
            "changed_mind",
            "wrong_item"
        ],
        "auto_approve_conditions": {
            "defective": True,
            "wrong_item": True
        },
        "restocking_fee": 0.0
    }
```

#### Implementation Example
```python
class FulfillmentAgent(BaseProductAgent):
    """Agent responsible for order fulfillment and inventory management."""
    
    def __init__(self, product_id: str, config: FulfillmentAgentConfig):
        super().__init__(product_id, "fulfillment")
        self.config = config
        self.shopify = ShopifyAPI(config.store_url)
        self.inventory_forecaster = InventoryForecaster()
        self.supplier_client = self._init_supplier_client()
        
    async def process_new_order(self, order: Order) -> FulfillmentResult:
        """Process a new order from creation to shipment."""
        
        # Fraud check if enabled
        if self.config.order_processing["fraud_check"]["enabled"]:
            fraud_result = await self._check_fraud(order)
            if fraud_result.risk_level == "high":
                return await self._flag_for_review(order, fraud_result)
                
        # Check inventory
        inventory_check = await self._check_inventory(order.items)
        if not inventory_check.in_stock:
            # Try to fulfill from backup supplier
            backup_result = await self._try_backup_fulfillment(order)
            if not backup_result.success:
                return FulfillmentResult(
                    status="failed",
                    reason="out_of_stock",
                    estimated_restock=inventory_check.restock_date
                )
                
        # Create fulfillment
        fulfillment = await self.shopify.create_fulfillment(
            order_id=order.id,
            tracking_company=self.config.shipping_config["default_carrier"],
            notify_customer=self.config.shipping_config["tracking_notification"]
        )
        
        # Update inventory
        await self._update_inventory(order.items)
        
        # Check if reorder needed
        await self._check_reorder_needed()
        
        return FulfillmentResult(
            status="success",
            fulfillment_id=fulfillment.id,
            tracking_number=fulfillment.tracking_number,
            estimated_delivery=fulfillment.estimated_delivery
        )
        
    async def monitor_inventory_levels(self) -> InventoryStatus:
        """Continuously monitor and predict inventory needs."""
        
        # Get current inventory levels
        current_inventory = await self.shopify.get_inventory_levels(self.product_id)
        
        # Get recent sales data
        sales_history = await self._get_sales_history(days=30)
        
        # Forecast future demand
        demand_forecast = await self.inventory_forecaster.predict(
            sales_history=sales_history,
            method=self.config.inventory_config["forecasting_method"],
            horizon_days=30
        )
        
        # Calculate reorder point
        reorder_point = self._calculate_reorder_point(
            daily_demand=demand_forecast.avg_daily_demand,
            lead_time=self.config.supplier_config["primary_supplier"]["lead_time_days"],
            safety_factor=self.config.inventory_config["safety_stock_multiplier"]
        )
        
        # Determine if reorder needed
        if current_inventory.available <= reorder_point:
            reorder_quantity = self._calculate_reorder_quantity(
                demand_forecast=demand_forecast,
                current_inventory=current_inventory,
                constraints={
                    "moq": self.config.supplier_config["primary_supplier"]["moq"],
                    "max_stock_days": self.config.inventory_config["max_stock_days"]
                }
            )
            
            # Create reorder
            await self._create_purchase_order(reorder_quantity)
            
        return InventoryStatus(
            current_level=current_inventory.available,
            reorder_point=reorder_point,
            days_of_stock=current_inventory.available / demand_forecast.avg_daily_demand,
            forecast=demand_forecast
        )
        
    async def handle_return_request(self, return_request: ReturnRequest) -> ReturnResult:
        """Process customer return requests."""
        
        # Validate return window
        order_date = await self._get_order_date(return_request.order_id)
        if (datetime.now() - order_date).days > self.config.returns_config["return_window_days"]:
            return ReturnResult(
                approved=False,
                reason="outside_return_window"
            )
            
        # Auto-approve if conditions met
        if return_request.reason in self.config.returns_config["auto_approve_conditions"]:
            if self.config.returns_config["auto_approve_conditions"][return_request.reason]:
                return await self._process_return(return_request, auto_approved=True)
                
        # Otherwise, create checkpoint for human review
        checkpoint = await self._create_return_checkpoint(return_request)
        
        return ReturnResult(
            status="pending_review",
            checkpoint_id=checkpoint.id
        )
        
    async def _create_purchase_order(self, quantity: int) -> PurchaseOrder:
        """Create a purchase order with the supplier."""
        
        supplier = self.config.supplier_config["primary_supplier"]
        
        if supplier["type"] == "api":
            # API-based ordering
            po = await self.supplier_client.create_order(
                product_sku=self.product_id,
                quantity=quantity,
                shipping_address=self._get_warehouse_address()
            )
        else:
            # Email-based ordering
            po = await self._create_email_purchase_order(supplier, quantity)
            
        # Record in system
        await self._record_purchase_order(po)
        
        # Set up tracking
        await self._track_purchase_order(po)
        
        return po
```

---

## Inter-Agent Communication Protocol

### Message Format

```python
@dataclass
class AgentMessage:
    """Standard message format for inter-agent communication."""
    
    # Message metadata
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Routing information
    from_agent: str  # Agent type (e.g., "image_generation")
    to_agent: str    # Target agent or "broadcast"
    product_id: str  # Product instance this relates to
    
    # Message content
    message_type: MessageType  # REQUEST, RESPONSE, EVENT, ERROR
    action: str  # Specific action requested/performed
    payload: Dict[str, Any]  # Message data
    
    # Context and tracking
    correlation_id: Optional[str] = None  # For request/response pairs
    priority: Priority = Priority.NORMAL
    ttl: Optional[int] = None  # Time to live in seconds
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
```

### Communication Patterns

#### 1. Request-Response Pattern
```python
# Image agent requests product data from content agent
request = AgentMessage(
    from_agent="image_generation",
    to_agent="content",
    product_id="prod_123",
    message_type=MessageType.REQUEST,
    action="get_product_description",
    payload={"format": "structured", "include_features": True}
)

# Content agent responds
response = AgentMessage(
    from_agent="content",
    to_agent="image_generation",
    product_id="prod_123",
    message_type=MessageType.RESPONSE,
    action="product_description",
    correlation_id=request.id,
    payload={
        "title": "Eco-Friendly Water Bottle",
        "features": ["BPA-free", "Insulated", "Leak-proof"],
        "description": "..."
    }
)
```

#### 2. Event Broadcasting
```python
# Fulfillment agent broadcasts low inventory event
event = AgentMessage(
    from_agent="fulfillment",
    to_agent="broadcast",
    product_id="prod_123",
    message_type=MessageType.EVENT,
    action="low_inventory_alert",
    priority=Priority.HIGH,
    payload={
        "current_stock": 50,
        "reorder_point": 100,
        "daily_velocity": 10
    }
)

# Multiple agents can react:
# - Advertisement agent might reduce ad spend
# - Analytics agent logs the event
# - Orchestrator notifies the user
```

#### 3. Workflow Coordination
```python
class AgentCoordinator:
    """Coordinates multi-agent workflows."""
    
    async def coordinate_product_launch(self, product_id: str):
        """Coordinate agents for product launch."""
        
        # Phase 1: Content preparation
        content_tasks = [
            self.send_message(
                to_agent="content",
                action="generate_all_content",
                payload={"product_id": product_id}
            ),
            self.send_message(
                to_agent="image_generation",
                action="generate_image_set",
                payload={"product_id": product_id}
            )
        ]
        
        content_results = await asyncio.gather(*content_tasks)
        
        # Phase 2: Marketing preparation (depends on content)
        marketing_tasks = [
            self.send_message(
                to_agent="video_generation",
                action="create_launch_video",
                payload={
                    "product_id": product_id,
                    "images": content_results[1].payload["images"]
                }
            ),
            self.send_message(
                to_agent="advertisement",
                action="prepare_launch_campaigns",
                payload={
                    "product_id": product_id,
                    "content": content_results[0].payload
                }
            )
        ]
        
        marketing_results = await asyncio.gather(*marketing_tasks)
        
        # Phase 3: Go live
        launch_message = self.send_message(
            to_agent="fulfillment",
            action="activate_product",
            payload={"product_id": product_id}
        )
        
        return await launch_message
```

### Message Queue Implementation

```python
class AgentMessageBroker:
    """Central message broker for agent communication."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.subscribers = defaultdict(list)
        
    async def publish(self, message: AgentMessage):
        """Publish message to appropriate channels."""
        
        # Store message for tracking
        await self.redis.set(
            f"message:{message.id}",
            message.to_json(),
            ex=3600  # 1 hour TTL
        )
        
        # Route based on destination
        if message.to_agent == "broadcast":
            # Publish to product-specific broadcast channel
            channel = f"product:{message.product_id}:broadcast"
        else:
            # Direct message to specific agent
            channel = f"product:{message.product_id}:agent:{message.to_agent}"
            
        await self.redis.publish(channel, message.to_json())
        
        # Handle priority messages
        if message.priority == Priority.HIGH:
            await self._handle_priority_message(message)
            
    async def subscribe(self, agent_type: str, product_id: str, callback: Callable):
        """Subscribe agent to messages."""
        
        channels = [
            f"product:{product_id}:agent:{agent_type}",  # Direct messages
            f"product:{product_id}:broadcast"  # Broadcast messages
        ]
        
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                agent_message = AgentMessage.from_json(message['data'])
                await callback(agent_message)
```

---

## Customization Framework

### Frontend-Editable Configuration

#### 1. Prompt Template System

```python
class PromptTemplate(BaseModel):
    """Editable prompt template."""
    
    id: str
    agent_type: str
    action: str
    template: str
    variables: List[str]  # Required variables
    examples: List[Dict[str, Any]]
    version: int
    last_modified: datetime
    modified_by: str
    
    def render(self, **kwargs) -> str:
        """Render template with variables."""
        return self.template.format(**kwargs)

class PromptManager:
    """Manages customizable prompts for agents."""
    
    def __init__(self, db_session):
        self.db = db_session
        
    async def get_prompt(self, agent_type: str, action: str, product_id: str) -> str:
        """Get customized prompt for specific action."""
        
        # Try product-specific prompt first
        custom_prompt = await self.db.query(
            "SELECT * FROM custom_prompts WHERE product_id = ? AND agent_type = ? AND action = ?",
            [product_id, agent_type, action]
        )
        
        if custom_prompt:
            return PromptTemplate(**custom_prompt).render
            
        # Fall back to default template
        default_prompt = await self.db.query(
            "SELECT * FROM prompt_templates WHERE agent_type = ? AND action = ?",
            [agent_type, action]
        )
        
        return PromptTemplate(**default_prompt).render
        
    async def update_prompt(self, product_id: str, agent_type: str, action: str, 
                          new_template: str, user_id: str):
        """Update prompt template for a product."""
        
        # Validate template
        validation_result = await self._validate_template(new_template, agent_type, action)
        if not validation_result.valid:
            raise ValueError(f"Invalid template: {validation_result.error}")
            
        # Save to database
        await self.db.execute(
            """
            INSERT INTO custom_prompts (product_id, agent_type, action, template, modified_by, modified_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (product_id, agent_type, action) 
            DO UPDATE SET template = ?, modified_by = ?, modified_at = ?
            """,
            [product_id, agent_type, action, new_template, user_id, datetime.utcnow()]
        )
        
        # Notify agent of update
        await self._notify_agent_update(product_id, agent_type)
```

#### 2. Agent Parameter Configuration

```python
class AgentParameterConfig:
    """Manages agent parameter customization."""
    
    def __init__(self):
        self.parameter_schemas = {
            "image_generation": ImageAgentConfig,
            "video_generation": VideoAgentConfig,
            "advertisement": AdvertisementAgentConfig,
            "fulfillment": FulfillmentAgentConfig
        }
        
    async def get_config_schema(self, agent_type: str) -> Dict:
        """Get configuration schema for frontend form generation."""
        
        schema = self.parameter_schemas[agent_type]
        return self._pydantic_to_json_schema(schema)
        
    async def update_config(self, product_id: str, agent_type: str, 
                          config_updates: Dict, user_id: str):
        """Update agent configuration."""
        
        # Get current config
        current_config = await self._get_current_config(product_id, agent_type)
        
        # Validate updates against schema
        schema = self.parameter_schemas[agent_type]
        updated_config = schema(**{**current_config, **config_updates})
        
        # Save to database
        await self._save_config(product_id, agent_type, updated_config.dict())
        
        # Hot-reload agent with new config
        await self._reload_agent(product_id, agent_type, updated_config)
```

#### 3. Frontend API Endpoints

```python
# Additional API routes for customization

@router.get("/products/{product_id}/agents/{agent_type}/config")
async def get_agent_config(product_id: str, agent_type: str):
    """Get current agent configuration."""
    config = await agent_config_manager.get_config(product_id, agent_type)
    schema = await agent_config_manager.get_config_schema(agent_type)
    
    return {
        "current_config": config,
        "schema": schema,
        "editable_fields": schema.get("editable_fields", [])
    }

@router.put("/products/{product_id}/agents/{agent_type}/config")
async def update_agent_config(
    product_id: str, 
    agent_type: str,
    updates: Dict,
    user: User = Depends(get_current_user)
):
    """Update agent configuration."""
    await agent_config_manager.update_config(
        product_id, agent_type, updates, user.id
    )
    return {"status": "updated"}

@router.get("/products/{product_id}/agents/{agent_type}/prompts")
async def get_agent_prompts(product_id: str, agent_type: str):
    """Get all prompts for an agent."""
    prompts = await prompt_manager.get_all_prompts(product_id, agent_type)
    return prompts

@router.put("/products/{product_id}/agents/{agent_type}/prompts/{action}")
async def update_agent_prompt(
    product_id: str,
    agent_type: str,
    action: str,
    prompt_update: PromptUpdate,
    user: User = Depends(get_current_user)
):
    """Update specific prompt template."""
    await prompt_manager.update_prompt(
        product_id, agent_type, action, 
        prompt_update.template, user.id
    )
    return {"status": "updated"}
```

---

## Database Schema

### New Tables for Product Lifecycle

```sql
-- Product instances table (extends existing products table)
ALTER TABLE products ADD COLUMN lifecycle_stage VARCHAR(50) DEFAULT 'discovery';
ALTER TABLE products ADD COLUMN instance_config JSONB;
ALTER TABLE products ADD COLUMN active_agents TEXT[];

-- Agent configurations per product
CREATE TABLE agent_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    config_data JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(product_id, agent_type)
);

-- Custom prompts per product
CREATE TABLE custom_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    template TEXT NOT NULL,
    variables TEXT[], -- Required variables
    examples JSONB,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_by UUID REFERENCES users(id),
    UNIQUE(product_id, agent_type, action)
);

-- Agent execution history
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50), -- success, failed, timeout
    error_message TEXT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 4),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    correlation_id UUID -- For tracking related executions
);

-- Inter-agent messages
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    from_agent VARCHAR(50) NOT NULL,
    to_agent VARCHAR(50) NOT NULL,
    message_type VARCHAR(20), -- REQUEST, RESPONSE, EVENT, ERROR
    action VARCHAR(100),
    payload JSONB,
    priority VARCHAR(10) DEFAULT 'NORMAL',
    correlation_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    ttl_seconds INTEGER
);

-- Generated content storage
CREATE TABLE generated_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    content_type VARCHAR(50), -- image, video, ad_copy, etc.
    agent_type VARCHAR(50),
    content_data JSONB, -- URLs, text, metadata
    platform VARCHAR(50), -- youtube, tiktok, instagram, etc.
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    performance_data JSONB, -- CTR, conversions, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) -- agent_type that created it
);

-- Campaign management
CREATE TABLE advertising_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- facebook, google, tiktok
    campaign_id_external VARCHAR(255), -- Platform's campaign ID
    campaign_name VARCHAR(255),
    status VARCHAR(50), -- active, paused, completed
    budget_daily DECIMAL(10, 2),
    budget_total DECIMAL(10, 2),
    spent_total DECIMAL(10, 2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    targeting_data JSONB,
    creative_data JSONB,
    performance_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fulfillment tracking
CREATE TABLE fulfillment_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id),
    order_id_external VARCHAR(255), -- Shopify order ID
    order_status VARCHAR(50),
    customer_data JSONB,
    items JSONB,
    tracking_number VARCHAR(255),
    carrier VARCHAR(50),
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    return_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory tracking
CREATE TABLE inventory_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    location VARCHAR(255) DEFAULT 'main',
    available INTEGER NOT NULL DEFAULT 0,
    incoming INTEGER DEFAULT 0,
    reserved INTEGER DEFAULT 0,
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    last_reorder_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, location)
);

-- Create indexes for performance
CREATE INDEX idx_agent_executions_product_agent ON agent_executions(product_id, agent_type);
CREATE INDEX idx_agent_messages_product_created ON agent_messages(product_id, created_at);
CREATE INDEX idx_generated_content_product_type ON generated_content(product_id, content_type);
CREATE INDEX idx_campaigns_product_platform ON advertising_campaigns(product_id, platform);
CREATE INDEX idx_fulfillment_product_status ON fulfillment_orders(product_id, order_status);
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
1. Create base `ProductInstance` class and lifecycle management
2. Implement `ProductOrchestrator` for agent coordination
3. Set up inter-agent communication protocol with Redis
4. Create database schema and migrations
5. Build basic agent configuration system

### Phase 2: Core Agents (Week 3-4)
1. Implement `ImageGenerationAgent` with DALL-E integration
2. Implement `FulfillmentAgent` with Shopify integration
3. Create basic `ContentGenerationAgent`
4. Set up agent message broker and routing

### Phase 3: Advanced Agents (Week 5-6)
1. Implement `VideoGenerationAgent` with Veo 3 integration
2. Implement `AdvertisementAgent` with Meta/Google Ads
3. Add analytics and monitoring capabilities
4. Create customization framework

### Phase 4: Frontend Integration (Week 7-8)
1. Build agent configuration UI
2. Create prompt editing interface
3. Implement real-time agent status monitoring
4. Add performance dashboards

### Phase 5: Testing & Optimization (Week 9-10)
1. End-to-end testing of product lifecycle
2. Performance optimization
3. Error handling and recovery
4. Documentation and training materials

## Success Metrics
- Time from opportunity approval to product launch
- Agent task success rate
- ROI per product instance
- User intervention frequency
- System resource utilization

## Conclusion

This implementation plan provides a comprehensive framework for managing product lifecycles through specialized AI agents. The system is designed to be highly customizable while maintaining operational efficiency, allowing each product to have its own optimized strategy while benefiting from shared learning and resources.