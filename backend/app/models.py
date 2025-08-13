from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PromptCategory(str, Enum):
    PROGRAMMING = "编程"
    WRITING = "写作"
    ANALYSIS = "分析"
    CREATIVE = "创意"
    BUSINESS = "商业"
    EDUCATION = "教育"
    OTHER = "其他"


class PromptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="提示词标题")
    content: str = Field(..., min_length=1, description="提示词内容")
    description: Optional[str] = Field(None, max_length=500, description="提示词描述")
    category: str = Field(default="其他", description="分类")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class Prompt(PromptBase):
    id: str
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    color: str = Field(default="#3B82F6", description="分类颜色")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = None


class Category(CategoryBase):
    id: str
    prompt_count: int = 0

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30, description="标签名称")
    color: str = Field(default="#6B7280", description="标签颜色")


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = None


class Tag(TagBase):
    id: str
    usage_count: int = 0

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    prompts: List[Prompt]
    total: int
    categories: List[Category]
    tags: List[Tag]


class StatsResponse(BaseModel):
    total_prompts: int
    total_categories: int
    total_tags: int
    most_used_prompt: Optional[Prompt] = None
    category_distribution: List[dict]
