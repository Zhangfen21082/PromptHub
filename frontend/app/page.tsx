'use client'

import { useState, useEffect } from 'react'
import { Plus, Search, Copy, Edit, Trash2, Tag, FolderOpen } from 'lucide-react'

interface Prompt {
  id: string
  title: string
  content: string
  description?: string
  category: string
  tags: string[]
  usage_count: number
  created_at: string
  updated_at: string
}

interface Category {
  id: string
  name: string
  color: string
  prompt_count: number
}

interface Tag {
  id: string
  name: string
  color: string
  usage_count: number
}

export default function Home() {
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [tags, setTags] = useState<Tag[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [promptsRes, categoriesRes, tagsRes] = await Promise.all([
        fetch('/api/v1/prompts'),
        fetch('/api/v1/categories'),
        fetch('/api/v1/tags')
      ])
      
      const promptsData = await promptsRes.json()
      const categoriesData = await categoriesRes.json()
      const tagsData = await tagsRes.json()
      
      setPrompts(promptsData)
      setCategories(categoriesData)
      setTags(tagsData)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      // 这里可以添加一个toast通知
      console.log('已复制到剪贴板')
    } catch (error) {
      console.error('复制失败:', error)
    }
  }

  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = searchQuery === '' || 
      prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      prompt.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (prompt.description && prompt.description.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesCategory = selectedCategory === '' || prompt.category === selectedCategory
    
    const matchesTags = selectedTags.length === 0 || 
      selectedTags.some(tag => prompt.tags.includes(tag))
    
    return matchesSearch && matchesCategory && matchesTags
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">加载中...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 头部 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">PromptHub</h1>
        <p className="text-gray-600">智能提示词管理平台</p>
      </div>

      {/* 搜索和筛选 */}
      <div className="mb-6 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="搜索提示词..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center gap-2">
            <Plus className="w-5 h-5" />
            添加提示词
          </button>
        </div>

        {/* 分类筛选 */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory('')}
            className={`px-3 py-1 rounded-full text-sm ${
              selectedCategory === '' 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            全部
          </button>
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.name)}
              className={`px-3 py-1 rounded-full text-sm flex items-center gap-1 ${
                selectedCategory === category.name 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: category.color }}
              />
              {category.name} ({category.prompt_count})
            </button>
          ))}
        </div>
      </div>

      {/* 提示词列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPrompts.map(prompt => (
          <div key={prompt.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-semibold text-gray-900">{prompt.title}</h3>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(prompt.content)}
                  className="p-1 text-gray-400 hover:text-primary-600"
                  title="复制"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button className="p-1 text-gray-400 hover:text-gray-600" title="编辑">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="p-1 text-gray-400 hover:text-red-600" title="删除">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {prompt.description && (
              <p className="text-gray-600 text-sm mb-3">{prompt.description}</p>
            )}
            
            <div className="mb-3">
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                <FolderOpen className="w-3 h-3" />
                {prompt.category}
              </span>
            </div>
            
            {prompt.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {prompt.tags.map(tag => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full"
                  >
                    <Tag className="w-3 h-3" />
                    {tag}
                  </span>
                ))}
              </div>
            )}
            
            <div className="text-xs text-gray-500">
              使用 {prompt.usage_count} 次 • 更新于 {new Date(prompt.updated_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>

      {filteredPrompts.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg">暂无提示词</div>
          <p className="text-gray-500 mt-2">开始添加你的第一个提示词吧！</p>
        </div>
      )}
    </div>
  )
}
