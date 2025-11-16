"""
Data Models for Advanced SEO Analysis
All data structures used across the SEO analysis system
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class SearchIntent(Enum):
    """Search intent types"""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    LOCAL = "local"
    COMPARISON = "comparison"
    NAVIGATIONAL = "navigational"


class FunnelLevel(Enum):
    """Marketing funnel levels"""
    TOFU = "top_of_funnel"  # Awareness
    MOFU = "middle_of_funnel"  # Consideration
    BOFU = "bottom_of_funnel"  # Conversion


class PageType(Enum):
    """Page type for schema selection"""
    HOME = "home"
    SERVICE = "service"
    LOCAL = "local"
    ARTICLE = "article"
    PRODUCT = "product"
    PORTFOLIO = "portfolio"
    VIDEO = "video"
    FAQ = "faq"


class ActionType(Enum):
    """Content gap action types"""
    CREATE = "create"
    UPDATE = "update"
    MERGE = "merge"
    DELETE = "delete"
    REDIRECT = "redirect"


class SERPFeatureType(Enum):
    """SERP feature types"""
    FAQ = "faq"
    HOWTO = "howto"
    FEATURED_SNIPPET = "featured_snippet"
    SITELINKS = "sitelinks"
    VIDEO = "video"
    IMAGE_PACK = "image_pack"
    LOCAL_PACK = "local_pack"
    KNOWLEDGE_PANEL = "knowledge_panel"
    TOP_STORIES = "top_stories"
    PEOPLE_ALSO_ASK = "people_also_ask"


# ==================== Competitor Analysis ====================

@dataclass
class SERPFeature:
    """SERP feature detected for a competitor"""
    type: SERPFeatureType
    present: bool
    content: Optional[str] = None
    schema_type: Optional[str] = None


@dataclass
class ValueProposition:
    """Value proposition/angle of competitor content"""
    primary_angle: str  # doctor-focused, device-focused, price-focused, etc.
    secondary_angles: List[str] = field(default_factory=list)
    unique_elements: List[str] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class TopicalCoverage:
    """Topics covered by competitor"""
    main_topics: List[str] = field(default_factory=list)
    subtopics: List[str] = field(default_factory=list)
    missing_topics: List[str] = field(default_factory=list)  # Compared to others
    depth_score: float = 0.0  # 0-100


@dataclass
class HeadingNode:
    """Hierarchical heading structure"""
    level: int  # 1-6
    text: str
    children: List['HeadingNode'] = field(default_factory=list)
    word_count_after: int = 0  # Estimated paragraph length after this heading


@dataclass
class InternalLinkingQuality:
    """Internal linking metrics for competitor"""
    click_depth: int
    is_hub_page: bool
    is_spoke_page: bool
    incoming_links_count: int
    outgoing_links_count: int
    anchor_text_distribution: Dict[str, int] = field(default_factory=dict)  # exact/partial/branded/generic
    orphan_status: bool = False


@dataclass
class CompetitorProfile:
    """Enhanced competitor profile with all new metrics"""
    url: str
    rank: int
    domain: str
    
    # Basic SEO
    title: str
    meta_description: str
    h1_tags: List[str]
    word_count: int
    
    # New: Intent & SERP
    search_intent: SearchIntent
    serp_features: List[SERPFeature] = field(default_factory=list)
    value_proposition: Optional[ValueProposition] = None
    
    # New: Content Analysis
    topical_coverage: Optional[TopicalCoverage] = None
    heading_map: List[HeadingNode] = field(default_factory=list)
    
    # New: Link Quality
    internal_linking_quality: Optional[InternalLinkingQuality] = None
    
    # Existing metrics
    images_count: int = 0
    page_speed_score: float = 0.0
    mobile_ux_score: float = 0.0
    has_schema: bool = False
    schema_types: List[str] = field(default_factory=list)
    
    # Raw data reference
    raw_data: Dict[str, Any] = field(default_factory=dict)


# ==================== Keyword Clustering ====================

@dataclass
class KeywordMetrics:
    """Keyword performance metrics"""
    search_volume: int = 0
    difficulty: float = 0.0  # 0-100
    cpc: float = 0.0
    competition: float = 0.0  # 0-1
    trend: str = "stable"  # rising/stable/declining


@dataclass
class KeywordCluster:
    """Semantic keyword cluster with metadata"""
    cluster_id: str
    cluster_name: str
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    
    # Intent & Funnel
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    funnel_level: FunnelLevel = FunnelLevel.TOFU
    
    # Metrics
    metrics: Optional[KeywordMetrics] = None
    
    # E-E-A-T Keywords
    eeat_keywords: List[str] = field(default_factory=list)  # doctor names, credentials, etc.
    
    # Questions
    paa_questions: List[str] = field(default_factory=list)  # People Also Ask
    autofill_suggestions: List[str] = field(default_factory=list)
    
    # Local
    geo_modifiers: List[str] = field(default_factory=list)  # cities, neighborhoods
    
    # Schema recommendations
    recommended_schemas: List[str] = field(default_factory=list)
    
    # SERP features to target
    serp_features_to_target: List[SERPFeatureType] = field(default_factory=list)
    
    # Priority
    priority_score: float = 0.0  # RICE or ICE score
    effort_estimate_hours: float = 0.0
    estimated_ttf: int = 0  # Time to first page (days)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


# ==================== Content Brief ====================

@dataclass
class MediaSlot:
    """Image or video slot in content"""
    slot_name: str  # hero, device_alex, gallery_1, etc.
    media_type: str  # image/video
    alt_text: str
    caption: Optional[str] = None
    recommended_size: Optional[str] = None  # 1600x900
    file_format: Optional[str] = None  # webp, jpg, mp4


@dataclass
class InternalLinkSuggestion:
    """Internal link to add"""
    anchor_text: str
    target_url: str
    placement: str  # after_h2_1, in_paragraph_3, etc.
    relevance_score: float = 0.0


@dataclass
class CTAConfig:
    """Call-to-action configuration"""
    type: str  # form/whatsapp/call/button
    location: str  # after_h2_3, sidebar, floating, etc.
    fields: List[str] = field(default_factory=list)  # name, phone, area, etc.
    button_text: str = "رزرو نوبت"


@dataclass
class OutlineSection:
    """Section in content outline"""
    heading_level: int  # 2 or 3
    heading_text: str
    paragraph_length_words: int = 150
    include_image: bool = False
    include_video: bool = False
    subsections: List['OutlineSection'] = field(default_factory=list)


@dataclass
class ContentBrief:
    """Complete content brief - ready for writers"""
    brief_id: str
    cluster: KeywordCluster
    
    # Target
    target_url: str
    page_type: PageType
    
    # SEO Meta
    title_tag: str
    meta_description: str
    h1: str
    
    # Content Structure
    outline: List[OutlineSection] = field(default_factory=list)
    estimated_word_count: int = 0
    
    # Media Plan
    media_plan: List[MediaSlot] = field(default_factory=list)
    
    # FAQ
    faq_items: List[Dict[str, str]] = field(default_factory=list)  # question/answer pairs
    
    # Links
    internal_links: List[InternalLinkSuggestion] = field(default_factory=list)
    external_references: List[str] = field(default_factory=list)  # Authority sources
    
    # Schema
    schema_pack: List[str] = field(default_factory=list)  # Schema types to implement
    
    # CTA
    cta_config: Optional[CTAConfig] = None
    
    # Trust Elements
    trust_elements: List[str] = field(default_factory=list)  # doctor profile, credentials, etc.
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    status: str = "draft"  # draft/in_progress/review/approved


# ==================== Content Gap ====================

@dataclass
class ContentGapAction:
    """Action item from content gap analysis"""
    action_id: str
    action_type: ActionType
    
    # URLs
    url_suggested: Optional[str] = None  # For CREATE
    url_existing: Optional[str] = None  # For UPDATE/MERGE/DELETE
    url_target: Optional[str] = None  # For MERGE (merge into)
    
    # Context
    cluster: Optional[KeywordCluster] = None
    reason: str = ""
    issue_details: str = ""
    
    # What to do
    what_to_add: List[str] = field(default_factory=list)  # For UPDATE
    what_to_remove: List[str] = field(default_factory=list)
    
    # Brief
    brief_id: Optional[str] = None
    
    # Priority
    priority: str = "medium"  # low/medium/high/critical
    effort_estimate_hours: float = 0.0
    impact_score: float = 0.0  # 0-100
    
    # Status
    status: str = "pending"  # pending/in_progress/completed


# ==================== Schema Planning ====================

@dataclass
class SchemaField:
    """Schema field with auto-population"""
    field_name: str
    field_type: str  # Text/URL/Date/Organization/etc.
    required: bool
    value: Optional[Any] = None
    auto_populated: bool = False
    source: Optional[str] = None  # Where value came from


@dataclass
class SchemaPack:
    """Schema pack for a page"""
    page_url: str
    page_type: PageType
    
    schemas: List[Dict[str, Any]] = field(default_factory=list)  # type/status/fields
    auto_fields: Dict[str, str] = field(default_factory=dict)  # Populated from site data
    
    validation_status: str = "not_validated"  # not_validated/valid/has_errors
    validation_errors: List[str] = field(default_factory=list)
    
    json_ld_code: str = ""  # Ready-to-use code


# ==================== Internal Linking ====================

@dataclass
class LinkSuggestion:
    """Internal link suggestion"""
    from_url: str
    to_url: str
    anchor_text: str
    anchor_type: str  # exact/partial/branded/generic
    context: str  # Where to place it
    relevance_score: float = 0.0


@dataclass
class PageLinkProfile:
    """Link profile for a page"""
    url: str
    page_type: PageType
    
    is_hub: bool = False
    is_spoke: bool = False
    is_orphan: bool = False
    
    click_depth: int = 0
    incoming_links: int = 0
    outgoing_links: int = 0
    
    suggested_links: List[LinkSuggestion] = field(default_factory=list)


@dataclass
class InternalLinkingPlan:
    """Complete internal linking plan"""
    site_url: str
    pages: List[PageLinkProfile] = field(default_factory=list)
    orphan_pages: List[str] = field(default_factory=list)
    hub_pages: List[str] = field(default_factory=list)
    anchor_distribution: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


# ==================== Task Management ====================

@dataclass
class QAChecklistItem:
    """QA checklist item"""
    item: str
    checked: bool = False


@dataclass
class TaskTicket:
    """Task ticket for Jira/Asana"""
    task_id: str
    task_title: str
    task_type: str  # content_creation/update/technical_fix/schema
    
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    
    # Attachments
    brief_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    
    # Checklist
    qa_checklist: List[QAChecklistItem] = field(default_factory=list)
    
    # Links
    url: Optional[str] = None
    related_urls: List[str] = field(default_factory=list)
    
    # Status
    status: str = "backlog"  # backlog/todo/in_progress/review/done
    priority: str = "medium"  # low/medium/high/critical
    
    # Effort
    effort_hours: float = 0.0
    
    # KPIs
    success_kpis: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


# ==================== Export Functions ====================

def to_dict(obj) -> Dict[str, Any]:
    """Convert dataclass to dictionary"""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            if isinstance(value, Enum):
                result[field_name] = value.value
            elif isinstance(value, list):
                result[field_name] = [to_dict(item) if hasattr(item, '__dataclass_fields__') else item for item in value]
            elif isinstance(value, dict):
                result[field_name] = {k: to_dict(v) if hasattr(v, '__dataclass_fields__') else v for k, v in value.items()}
            elif hasattr(value, '__dataclass_fields__'):
                result[field_name] = to_dict(value)
            elif isinstance(value, datetime):
                result[field_name] = value.isoformat()
            else:
                result[field_name] = value
        return result
    return obj


# ==================== Keyword Gap Analysis ====================

class KeywordDifficulty(Enum):
    """Keyword difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class KeywordSource(Enum):
    """Source of keyword extraction"""
    TITLE = "title"
    META = "meta"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    CONTENT = "content"
    URL = "url"
    ALT_TEXT = "alt_text"
    ANCHOR_TEXT = "anchor_text"


@dataclass
class BusinessContext:
    """Business context for relevance scoring"""
    industry: str  # e.g., "healthcare", "ecommerce", "saas"
    niche: str  # e.g., "laser hair removal", "fashion retail"
    services: List[str] = field(default_factory=list)  # Specific services offered
    products: List[str] = field(default_factory=list)  # Specific products
    target_locations: List[str] = field(default_factory=list)  # Geographic targets
    brand_keywords: List[str] = field(default_factory=list)  # Brand names
    excluded_keywords: List[str] = field(default_factory=list)  # Keywords to exclude


@dataclass
class SearchQuery:
    """
    Enhanced keyword data structure representing a complete search query.
    This is a 'demand unit' not just a string.
    """
    # Core query
    query_text: str  # The actual search query
    
    # Intent & Context
    search_intent: SearchIntent = SearchIntent.INFORMATIONAL
    entity_context: Optional[str] = None  # e.g., "medical_service", "product_review"
    
    # Volume & Competition (estimated or from API)
    search_volume_estimate: int = 0  # Monthly searches
    difficulty: KeywordDifficulty = KeywordDifficulty.MEDIUM
    competition_score: float = 0.0  # 0-1
    
    # Relevance
    relevance_to_business: float = 0.0  # 0-1 score
    relevance_reasoning: str = ""  # Why this score
    
    # SERP Features
    serp_features: List[SERPFeatureType] = field(default_factory=list)
    recommended_content_type: PageType = PageType.ARTICLE
    
    # Extraction metadata
    source: KeywordSource = KeywordSource.CONTENT
    frequency: int = 1
    position_in_source: int = 0
    context_snippet: str = ""  # Surrounding text
    
    # Metrics
    tf_score: float = 0.0  # Term frequency
    idf_score: float = 0.0  # Inverse document frequency
    tfidf_score: float = 0.0  # TF-IDF combined
    
    # CTR & Value
    ctr_potential: float = 0.0  # 0-1 estimated CTR
    estimated_traffic_value: float = 0.0  # Monthly traffic potential
    
    # N-gram info
    ngram_size: int = 1  # Number of words in query
    is_long_tail: bool = False  # 3+ words
    
    # Competitors using this
    found_on_competitors: List[str] = field(default_factory=list)  # URLs of competitors
    competitor_avg_position: float = 0.0  # Average position on competitors
    
    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)


@dataclass
class KeywordGapOpportunity:
    """
    Represents a keyword gap opportunity with scoring and prioritization.
    """
    # The keyword
    query: SearchQuery
    
    # Gap analysis
    gap_type: str = "missing"  # missing / weak_presence / underoptimized
    
    # Visibility
    own_visibility: float = 0.0  # 0-1 (0 = not present, 1 = strong presence)
    competitor_visibility: float = 0.0  # 0-1 average across competitors
    visibility_gap: float = 0.0  # competitor - own
    
    # Opportunity Scoring (multi-dimensional)
    opportunity_score: float = 0.0  # Overall score 0-100
    
    # Score components
    volume_score: float = 0.0  # Based on search volume
    relevance_score: float = 0.0  # Based on business relevance
    difficulty_score: float = 0.0  # Inverse of difficulty (easier = higher score)
    intent_match_score: float = 0.0  # How well intent matches business model
    competition_score: float = 0.0  # Gap in competitor coverage
    
    # Priority Classification
    priority_tier: str = "medium"  # quick_win / high_priority / medium / long_term
    priority_reasoning: str = ""
    
    # Effort Estimation
    effort_estimate_hours: float = 0.0
    content_type_needed: PageType = PageType.ARTICLE
    
    # ROI Estimation
    estimated_monthly_traffic: int = 0
    estimated_conversions: float = 0.0
    estimated_revenue_impact: float = 0.0
    
    # Action Items
    recommended_actions: List[str] = field(default_factory=list)
    content_outline_suggestion: str = ""
    target_url_suggestion: str = ""
    
    # Competitors doing well
    top_competitor_urls: List[str] = field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class KeywordGapAnalysisResult:
    """
    Complete result of keyword gap analysis with business intelligence.
    """
    # Analysis context
    own_website_url: str
    competitor_urls: List[str] = field(default_factory=list)
    business_context: Optional[BusinessContext] = None
    
    # Keyword sets
    own_queries: List[SearchQuery] = field(default_factory=list)
    competitor_queries: Dict[str, List[SearchQuery]] = field(default_factory=dict)  # url -> queries
    
    # Gap opportunities
    gap_opportunities: List[KeywordGapOpportunity] = field(default_factory=list)
    
    # Categorized opportunities
    quick_wins: List[KeywordGapOpportunity] = field(default_factory=list)  # Easy + high relevance
    high_priority: List[KeywordGapOpportunity] = field(default_factory=list)  # High value
    medium_priority: List[KeywordGapOpportunity] = field(default_factory=list)
    long_term: List[KeywordGapOpportunity] = field(default_factory=list)  # Hard but valuable
    
    # Intent-based grouping
    informational_gaps: List[KeywordGapOpportunity] = field(default_factory=list)
    transactional_gaps: List[KeywordGapOpportunity] = field(default_factory=list)
    local_gaps: List[KeywordGapOpportunity] = field(default_factory=list)
    comparison_gaps: List[KeywordGapOpportunity] = field(default_factory=list)
    navigational_gaps: List[KeywordGapOpportunity] = field(default_factory=list)
    
    # Recommendations
    strategic_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    content_calendar_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Summary metrics
    total_gaps_found: int = 0
    total_opportunity_value: float = 0.0  # Sum of all estimated traffic
    avg_difficulty: float = 0.0
    avg_relevance: float = 0.0
    
    # Analysis metadata
    analysis_date: datetime = field(default_factory=datetime.now)
    analysis_version: str = "2.0"
    processing_time_seconds: float = 0.0


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Example: Create a keyword cluster
    cluster = KeywordCluster(
        cluster_id="cluster_001",
        cluster_name="لیزر موهای زائد غرب تهران",
        primary_keyword="لیزر موهای زائد سعادت‌آباد",
        secondary_keywords=["لیزر الکس تهران", "قیمت لیزر غرب تهران"],
        search_intent=SearchIntent.TRANSACTIONAL,
        funnel_level=FunnelLevel.BOFU,
        paa_questions=["لیزر الکس بهتره یا تیتانیوم؟", "چند جلسه لازم است؟"],
        geo_modifiers=["سعادت‌آباد", "شهرک غرب", "غرب تهران"],
        recommended_schemas=["FAQPage", "LocalBusiness", "Service"],
        priority_score=9.0,
        effort_estimate_hours=5.0
    )
    
    print("✅ Keyword Cluster created:")
    print(f"   {cluster.primary_keyword}")
    print(f"   Intent: {cluster.search_intent.value}")
    print(f"   Priority: {cluster.priority_score}")


