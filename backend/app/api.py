from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .models import (
    Prompt, PromptCreate, PromptUpdate, 
    Category, CategoryCreate, CategoryUpdate,
    Tag, TagCreate, TagUpdate, SearchResponse, StatsResponse
)
from .storage import FileStorage

router = APIRouter()
storage = FileStorage()


# 提示词相关API
@router.get("/prompts", response_model=List[Prompt])
async def get_prompts():
    """获取所有提示词"""
    return storage.get_all_prompts()


@router.get("/prompts/{prompt_id}", response_model=Prompt)
async def get_prompt(prompt_id: str):
    """根据ID获取提示词"""
    prompt = storage.get_prompt_by_id(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt


@router.post("/prompts", response_model=Prompt)
async def create_prompt(prompt: PromptCreate):
    """创建新提示词"""
    return storage.create_prompt(prompt)


@router.put("/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(prompt_id: str, prompt_update: PromptUpdate):
    """更新提示词"""
    prompt = storage.update_prompt(prompt_id, prompt_update)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """删除提示词"""
    success = storage.delete_prompt(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return {"message": "删除成功"}


@router.post("/prompts/{prompt_id}/use")
async def use_prompt(prompt_id: str):
    """使用提示词（增加使用次数）"""
    success = storage.increment_usage_count(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return {"message": "使用次数已更新"}


# 分类相关API
@router.get("/categories", response_model=List[Category])
async def get_categories():
    """获取所有分类"""
    return storage.get_all_categories()


@router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    """创建新分类"""
    return storage.create_category(category)


@router.put("/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, category_update: CategoryUpdate):
    """更新分类"""
    category = storage.update_category(category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    """删除分类"""
    success = storage.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "删除成功"}


# 标签相关API
@router.get("/tags", response_model=List[Tag])
async def get_tags():
    """获取所有标签"""
    return storage.get_all_tags()


@router.post("/tags", response_model=Tag)
async def create_tag(tag: TagCreate):
    """创建新标签"""
    return storage.create_tag(tag)


@router.put("/tags/{tag_id}", response_model=Tag)
async def update_tag(tag_id: str, tag_update: TagUpdate):
    """更新标签"""
    tag = storage.update_tag(tag_id, tag_update)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str):
    """删除标签"""
    success = storage.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="标签不存在")
    return {"message": "删除成功"}


# 搜索API
@router.get("/search", response_model=SearchResponse)
async def search_prompts(
    q: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    tags: Optional[str] = Query(None, description="标签筛选，用逗号分隔")
):
    """搜索提示词"""
    tag_list = tags.split(",") if tags else None
    
    prompts = storage.search_prompts(
        query=q or "",
        category=category or "",
        tags=tag_list
    )
    
    categories = storage.get_all_categories()
    all_tags = storage.get_all_tags()
    
    return SearchResponse(
        prompts=prompts,
        total=len(prompts),
        categories=categories,
        tags=all_tags
    )


# 统计API
@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """获取统计信息"""
    prompts = storage.get_all_prompts()
    categories = storage.get_all_categories()
    tags = storage.get_all_tags()
    
    # 最常用的提示词
    most_used_prompt = None
    if prompts:
        most_used_prompt = max(prompts, key=lambda p: p.usage_count)
    
    # 分类分布
    category_distribution = []
    for category in categories:
        count = len([p for p in prompts if p.category == category.name])
        category_distribution.append({
            "name": category.name,
            "count": count,
            "color": category.color
        })
    
    return StatsResponse(
        total_prompts=len(prompts),
        total_categories=len(categories),
        total_tags=len(tags),
        most_used_prompt=most_used_prompt,
        category_distribution=category_distribution
    )
