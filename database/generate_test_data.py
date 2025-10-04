#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成完善的测试数据
包括：多级分类、标签、提示词、版本历史
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.sqlite_storage import SQLiteStorage
from datetime import datetime, timedelta
import random

def generate_test_data():
    """生成完善的测试数据"""
    storage = SQLiteStorage()

    print("开始生成测试数据...")

    # 1. 创建分类树结构
    print("\n1. 创建分类体系...")
    categories = []

    # 一级分类
    cat_programming = storage.create_category({
        "name": "编程开发",
        "color": "#3B82F6",
        "description": "编程和软件开发相关提示词"
    })
    categories.append(cat_programming)

    cat_writing = storage.create_category({
        "name": "写作创作",
        "color": "#10B981",
        "description": "写作、文案、内容创作"
    })
    categories.append(cat_writing)

    cat_business = storage.create_category({
        "name": "商业分析",
        "color": "#EF4444",
        "description": "商业、市场、数据分析"
    })
    categories.append(cat_business)

    cat_learning = storage.create_category({
        "name": "学习教育",
        "color": "#8B5CF6",
        "description": "教育、学习、知识分享"
    })
    categories.append(cat_learning)

    # 二级分类 - 编程开发
    cat_python = storage.create_category({
        "name": "Python",
        "color": "#3776AB",
        "description": "Python 编程相关",
        "parent_id": cat_programming["id"]
    })

    cat_web = storage.create_category({
        "name": "Web开发",
        "color": "#F59E0B",
        "description": "前端和后端Web开发",
        "parent_id": cat_programming["id"]
    })

    cat_ai = storage.create_category({
        "name": "AI/机器学习",
        "color": "#06B6D4",
        "description": "人工智能和机器学习",
        "parent_id": cat_programming["id"]
    })

    # 三级分类 - Web开发
    cat_frontend = storage.create_category({
        "name": "前端开发",
        "color": "#F97316",
        "description": "HTML/CSS/JavaScript",
        "parent_id": cat_web["id"]
    })

    cat_backend = storage.create_category({
        "name": "后端开发",
        "color": "#84CC16",
        "description": "服务器端开发",
        "parent_id": cat_web["id"]
    })

    # 二级分类 - 写作创作
    cat_article = storage.create_category({
        "name": "文章写作",
        "color": "#14B8A6",
        "description": "博客、技术文章等",
        "parent_id": cat_writing["id"]
    })

    cat_marketing = storage.create_category({
        "name": "营销文案",
        "color": "#EC4899",
        "description": "广告、营销、推广文案",
        "parent_id": cat_writing["id"]
    })

    print(f"   创建了 {len(storage.get_all_categories())} 个分类")

    # 2. 创建标签
    print("\n2. 创建标签...")
    tags_data = [
        {"name": "代码生成", "color": "#3B82F6"},
        {"name": "代码审查", "color": "#10B981"},
        {"name": "Bug修复", "color": "#EF4444"},
        {"name": "性能优化", "color": "#F59E0B"},
        {"name": "API设计", "color": "#8B5CF6"},
        {"name": "SEO优化", "color": "#06B6D4"},
        {"name": "内容创作", "color": "#EC4899"},
        {"name": "数据分析", "color": "#14B8A6"},
        {"name": "教程编写", "color": "#F97316"},
        {"name": "文档生成", "color": "#84CC16"},
    ]

    tags = []
    for tag_data in tags_data:
        tag = storage.create_tag(tag_data)
        tags.append(tag)

    print(f"   创建了 {len(tags)} 个标签")

    # 3. 创建提示词
    print("\n3. 创建提示词...")

    prompts_data = [
        # Python 相关
        {
            "title": "Python 代码审查助手",
            "content": """你是一位经验丰富的 Python 开发者。请仔细审查以下代码，并提供：

1. 代码质量评估
2. 潜在的 bug 或问题
3. 性能优化建议
4. 最佳实践建议
5. 安全性问题

代码：
{code}

请提供详细的分析和改进建议。""",
            "description": "帮助审查 Python 代码，发现问题并提供优化建议",
            "category_id": cat_python["id"],
            "tags": ["代码审查", "Bug修复", "性能优化"]
        },
        {
            "title": "Python 数据分析脚本生成器",
            "content": """请根据以下需求生成 Python 数据分析脚本：

需求：{requirements}

请使用 pandas、numpy、matplotlib 等库，生成包含以下内容的完整脚本：
1. 数据加载和预处理
2. 数据探索性分析
3. 数据可视化
4. 统计分析
5. 结果总结

请确保代码有详细的注释。""",
            "description": "自动生成数据分析脚本",
            "category_id": cat_python["id"],
            "tags": ["代码生成", "数据分析"]
        },

        # 前端开发相关
        {
            "title": "React 组件生成器",
            "content": """作为一名资深的 React 开发者，请根据以下需求创建一个 React 组件：

组件需求：{requirements}

请提供：
1. 完整的组件代码（使用 TypeScript）
2. 组件的 Props 接口定义
3. 必要的样式（使用 CSS Modules 或 Tailwind）
4. 使用示例
5. 单元测试代码

请遵循 React 最佳实践和现代化的代码风格。""",
            "description": "快速生成符合最佳实践的 React 组件",
            "category_id": cat_frontend["id"],
            "tags": ["代码生成", "API设计"]
        },
        {
            "title": "CSS 性能优化顾问",
            "content": """你是 CSS 性能优化专家。请分析以下 CSS 代码并提供优化建议：

CSS 代码：
{css_code}

请提供：
1. 性能问题识别
2. 具体优化方案
3. 优化后的代码
4. 预期的性能提升
5. 浏览器兼容性注意事项""",
            "description": "分析和优化 CSS 性能",
            "category_id": cat_frontend["id"],
            "tags": ["性能优化", "代码审查"]
        },

        # 后端开发相关
        {
            "title": "RESTful API 设计助手",
            "content": """作为 API 设计专家，请为以下业务场景设计 RESTful API：

业务场景：{business_scenario}

请提供：
1. 完整的 API 端点设计
2. 请求/响应格式（JSON Schema）
3. HTTP 方法和状态码使用
4. 认证和授权方案
5. 错误处理机制
6. API 文档示例

请遵循 RESTful 最佳实践。""",
            "description": "设计符合最佳实践的 RESTful API",
            "category_id": cat_backend["id"],
            "tags": ["API设计", "文档生成"]
        },

        # AI/机器学习相关
        {
            "title": "机器学习模型选择顾问",
            "content": """你是机器学习专家。根据以下问题描述，推荐合适的机器学习模型：

问题描述：
- 任务类型：{task_type}
- 数据规模：{data_size}
- 数据特征：{data_features}
- 性能要求：{performance_requirements}

请提供：
1. 推荐的模型类型及原因
2. 模型优缺点分析
3. 数据预处理建议
4. 特征工程建议
5. 超参数调优策略
6. Python 实现示例（使用 scikit-learn 或 TensorFlow）""",
            "description": "根据具体场景推荐合适的机器学习模型",
            "category_id": cat_ai["id"],
            "tags": ["数据分析", "代码生成"]
        },

        # 文章写作相关
        {
            "title": "技术博客文章生成器",
            "content": """你是一位优秀的技术博客作者。请根据以下主题创作一篇技术文章：

主题：{topic}
目标读者：{target_audience}
文章长度：{word_count} 字左右

请包含：
1. 吸引人的标题
2. 简明的引言
3. 清晰的技术讲解（包含代码示例）
4. 实用的案例分析
5. 总结和要点回顾
6. SEO 友好的关键词

文章应该通俗易懂，技术准确，有实用价值。""",
            "description": "生成高质量的技术博客文章",
            "category_id": cat_article["id"],
            "tags": ["内容创作", "SEO优化", "教程编写"]
        },
        {
            "title": "教程文档编写助手",
            "content": """作为技术文档专家，请为以下技术主题创建完整的教程文档：

主题：{topic}
难度级别：{difficulty}

教程应包含：
1. 清晰的目录结构
2. 前置知识说明
3. 分步骤的详细讲解
4. 代码示例和注释
5. 常见问题和解决方案
6. 进阶学习资源

请确保教程结构清晰，易于理解和跟随。""",
            "description": "创建结构化的技术教程文档",
            "category_id": cat_article["id"],
            "tags": ["教程编写", "文档生成", "内容创作"]
        },

        # 营销文案相关
        {
            "title": "产品营销文案生成器",
            "content": """你是创意营销文案专家。请为以下产品创作营销文案：

产品信息：
- 产品名称：{product_name}
- 产品类型：{product_type}
- 目标用户：{target_users}
- 核心卖点：{key_features}
- 营销渠道：{marketing_channel}

请提供：
1. 3-5 个吸引人的标题
2. 简短有力的副标题
3. 产品描述（突出核心价值）
4. 行动号召（CTA）
5. SEO 关键词建议

文案应该有创意、有说服力、符合目标用户心理。""",
            "description": "创作有吸引力的产品营销文案",
            "category_id": cat_marketing["id"],
            "tags": ["内容创作", "SEO优化"]
        },

        # 商业分析相关
        {
            "title": "商业数据分析报告生成器",
            "content": """你是资深的商业数据分析师。请根据以下数据生成商业分析报告：

数据描述：{data_description}
分析目标：{analysis_goal}

报告应包含：
1. 执行摘要
2. 数据概览和趋势分析
3. 关键指标解读
4. 深度洞察和发现
5. 商业建议
6. 风险评估
7. 下一步行动计划

请使用图表来可视化关键数据，提供可执行的商业建议。""",
            "description": "生成专业的商业数据分析报告",
            "category_id": cat_business["id"],
            "tags": ["数据分析", "文档生成"]
        },

        # 学习教育相关
        {
            "title": "概念解释专家",
            "content": """你是优秀的教育者。请用简单易懂的方式解释以下概念：

概念：{concept}
目标受众：{audience_level}

解释应包含：
1. 简明定义
2. 通俗的比喻或类比
3. 实际应用场景
4. 图示说明（用文字描述）
5. 相关概念的联系
6. 学习资源推荐

请确保解释清晰、准确、易于理解。""",
            "description": "用通俗易懂的方式解释复杂概念",
            "category_id": cat_learning["id"],
            "tags": ["教程编写", "内容创作"]
        },

        # 未分类的通用提示词
        {
            "title": "问题解决框架",
            "content": """你是问题解决专家。请使用结构化的方法分析和解决以下问题：

问题描述：{problem}

请按以下框架进行分析：

1. 问题定义
   - 核心问题是什么？
   - 问题的范围和边界？

2. 现状分析
   - 当前情况如何？
   - 已知的信息和限制条件？

3. 根因分析
   - 可能的原因有哪些？
   - 主要原因是什么？

4. 解决方案
   - 提出 3 个可行方案
   - 每个方案的优缺点

5. 行动计划
   - 推荐方案
   - 具体实施步骤
   - 预期结果和风险

请提供系统化、可操作的分析。""",
            "description": "使用结构化方法分析和解决问题",
            "category_id": "0",  # 未分类
            "tags": ["数据分析"]
        },
    ]

    created_prompts = []
    base_time = datetime.now() - timedelta(days=30)

    for i, prompt_data in enumerate(prompts_data):
        # 创建提示词
        created_at = base_time + timedelta(days=i*2, hours=random.randint(0, 23))

        prompt = storage.create_prompt({
            "title": prompt_data["title"],
            "content": prompt_data["content"],
            "description": prompt_data["description"],
            "category_id": prompt_data["category_id"],
            "tags": prompt_data["tags"]
        })

        created_prompts.append(prompt)

        # 为部分提示词添加版本历史
        if i % 3 == 0:  # 每3个提示词中有1个有版本历史
            # 添加 1.1 版本
            storage.create_prompt_version(
                prompt["id"],
                {
                    "version": "1.1",
                    "title": prompt_data["title"],
                    "content": prompt_data["content"] + "\n\n更新：添加了更多细节和示例。",
                    "description": prompt_data["description"] + "（已优化）",
                    "change_note": "优化了提示词结构，添加了更多使用示例"
                }
            )

            # 添加 1.2 版本
            storage.create_prompt_version(
                prompt["id"],
                {
                    "version": "1.2",
                    "title": prompt_data["title"] + " Pro",
                    "content": prompt_data["content"] + "\n\n更新：增强了输出格式要求和质量控制。",
                    "description": prompt_data["description"] + "（专业版）",
                    "change_note": "重大更新：增强了输出质量，添加了格式控制"
                }
            )

            # 更新当前版本
            storage.update_prompt(prompt["id"], {"current_version": "1.2"})

        # 随机设置使用次数
        usage_count = random.randint(0, 50)
        if usage_count > 0:
            storage.update_prompt(prompt["id"], {"usage_count": usage_count})

    print(f"   创建了 {len(created_prompts)} 个提示词")
    print(f"   其中 {len([p for i, p in enumerate(created_prompts) if i % 3 == 0])} 个包含版本历史")

    # 4. 显示统计信息
    print("\n" + "="*50)
    print("测试数据生成完成！")
    print("="*50)

    all_categories = storage.get_all_categories()
    all_tags = storage.get_all_tags()
    all_prompts = storage.get_all_prompts()

    print(f"\n📊 数据统计：")
    print(f"   分类总数：{len(all_categories)}")
    print(f"   标签总数：{len(all_tags)}")
    print(f"   提示词总数：{len(all_prompts)}")

    # 按分类统计提示词数量
    print(f"\n📁 分类详情：")
    categories_tree = storage.get_categories_tree()

    def print_category_tree(cats, level=0):
        for cat in cats:
            indent = "  " * level
            prompt_count = len([p for p in all_prompts if p.get("category_id") == cat["id"]])
            print(f"   {indent}└─ {cat['name']} ({prompt_count} 个提示词)")
            if cat.get("children"):
                print_category_tree(cat["children"], level + 1)

    print_category_tree(categories_tree)

    # 标签统计
    print(f"\n🏷️  标签详情：")
    for tag in all_tags[:5]:  # 只显示前5个
        tagged_prompts = [p for p in all_prompts if tag["name"] in p.get("tags", [])]
        print(f"   • {tag['name']}: {len(tagged_prompts)} 个提示词")
    print(f"   ... 以及其他 {len(all_tags) - 5} 个标签")

    # 热门提示词
    print(f"\n🔥 热门提示词 TOP 5：")
    sorted_prompts = sorted(all_prompts, key=lambda x: x.get("usage_count", 0), reverse=True)
    for i, prompt in enumerate(sorted_prompts[:5], 1):
        print(f"   {i}. {prompt['title']} (使用 {prompt.get('usage_count', 0)} 次)")

    print(f"\n✅ 测试数据已成功生成到数据库！")

if __name__ == "__main__":
    generate_test_data()
