import React, { useState, useRef } from 'react'
import { GripVertical, Settings, Users, MessageSquare, Shield, Eye, Trash2, Bell, Hash, Layout, Plus, X } from 'lucide-react'

// 元件库面板
const componentLibrary = [
  { id: 'welcome-card', name: '歡迎卡片', icon: Bell, category: '訊息' },
  { id: 'verify-panel', name: '驗證面板', icon: Shield, category: '功能' },
  { id: 'member-list', name: '成員列表', icon: Users, category: '功能' },
  { id: 'chat-log', name: '訊息日誌', icon: MessageSquare, category: '功能' },
  { id: 'keyword-filter', name: '關鍵字過濾', icon: Hash, category: '功能' },
  { id: 'auto-delete', name: '自動刪除', icon: Trash2, category: '功能' },
  { id: 'stats-card', name: '統計卡片', icon: Eye, category: '資訊' },
  { id: 'button-grid', name: '按鈕選單', icon: Layout, category: '介面' },
  { id: 'topic-panel', name: '話題面板', icon: MessageSquare, category: '介面' },
  { id: 'admin-controls', name: '管理控制台', icon: Settings, category: '管理' },
]

export default function BotBuilder() {
  const [canvasItems, setCanvasItems] = useState([])
  const [selectedItem, setSelectedItem] = useState(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const canvasRef = useRef(null)

  // 开始拖拽元件
  const handleDragStart = (e, component) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left - 100
    const y = e.clientY - rect.top - 60
    
    const newItem = {
      id: Date.now(),
      type: component.id,
      name: component.name,
      x: Math.max(0, x),
      y: Math.max(0, y),
      width: 280,
      height: 180,
      config: {}
    }
    
    setCanvasItems([...canvasItems, newItem])
    setSelectedItem(newItem.id)
  }

  // 移动元件
  const handleItemMouseDown = (e, item) => {
    e.stopPropagation()
    setSelectedItem(item.id)
    const rect = e.target.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
  }

  // 画布鼠标移动
  const handleCanvasMouseMove = (e) => {
    if (!selectedItem) return
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left - dragOffset.x
    const y = e.clientY - rect.top - dragOffset.y
    
    setCanvasItems(items => items.map(item => 
      item.id === selectedItem 
        ? { ...item, x: Math.max(0, x), y: Math.max(0, y) }
        : item
    ))
  }

  // 删除元件
  const deleteItem = (id) => {
    setCanvasItems(items => items.filter(item => item.id !== id))
    if (selectedItem === id) setSelectedItem(null)
  }

  return (
    <div className="h-screen flex bg-slate-950 text-slate-100">
      
      {/* 左侧元件库 */}
      <div className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-5 border-b border-slate-800">
          <h2 className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-pink-400 bg-clip-text text-transparent">
            元件庫
          </h2>
          <p className="text-xs text-slate-500 mt-1">拖拽元件到畫布</p>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {['訊息', '功能', '資訊', '介面', '管理'].map(category => (
            <div key={category}>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">{category}</div>
              <div className="space-y-2">
                {componentLibrary.filter(c => c.category === category).map(component => (
                  <div
                    key={component.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, component)}
                    className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl hover:bg-slate-800 cursor-grab transition-all hover:scale-[1.02] border border-transparent hover:border-indigo-500/30 group"
                  >
                    <div className="w-9 h-9 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500/20">
                      <component.icon size={18} />
                    </div>
                    <span className="text-sm font-medium">{component.name}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 中间画布 - TG 预览 */}
      <div className="flex-1 p-8 overflow-auto bg-slate-950">
        <div className="max-w-xl mx-auto">
          {/* 手机模拟器 */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/10 to-pink-500/10 rounded-[3rem] blur-3xl" />
            
            <div 
              ref={canvasRef}
              className="relative w-full bg-gradient-to-b from-[#212121] to-[#171717] rounded-[3rem] p-2 shadow-2xl border border-slate-700/50"
              onMouseMove={handleCanvasMouseMove}
              onMouseUp={() => setSelectedItem(null)}
              onMouseLeave={() => setSelectedItem(null)}
            >
              {/* 顶部刘海 */}
              <div className="absolute top-3 left-1/2 -translate-x-1/2 w-32 h-6 bg-black rounded-full z-10" />
              
              {/* Telegram 界面 */}
              <div className="bg-[#212121] rounded-[2.5rem] overflow-hidden min-h-[720px]">
                {/* TG 头部 */}
                <div className="bg-[#17212b] px-6 py-4 flex items-center justify-between border-b border-slate-800/50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400" />
                    <div>
                      <div className="font-semibold text-white">初玖社群</div>
                      <div className="text-xs text-slate-400">1,247 成員 在線 89</div>
                    </div>
                  </div>
                  <div className="text-slate-400">⋯</div>
                </div>

                {/* 聊天画布区域 */}
                <div className="relative min-h-[580px] bg-[#0e1621] p-4">
                  {canvasItems.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/50 flex items-center justify-center text-slate-500">
                          <Plus size={28} />
                        </div>
                        <div className="text-slate-500 text-sm">從左側拖拽元件到這裡</div>
                        <div className="text-slate-600 text-xs mt-1">設計你的 Telegram 機器人介面</div>
                      </div>
                    </div>
                  )}

                  {/* 已放置的元件 */}
                  {canvasItems.map(item => (
                    <div
                      key={item.id}
                      className={`absolute bg-slate-800/90 rounded-2xl border-2 transition-all cursor-move select-none ${selectedItem === item.id ? 'border-indigo-400 ring-4 ring-indigo-400/20 z-20' : 'border-slate-700/50 hover:border-slate-600'}`}
                      style={{
                        left: item.x,
                        top: item.y,
                        width: item.width,
                        padding: 16
                      }}
                      onMouseDown={(e) => handleItemMouseDown(e, item)}
                    >
                      <div className="absolute -top-3 -right-3 opacity-0 group-hover:opacity-100">
                        <button 
                          onClick={() => deleteItem(item.id)}
                          className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-white shadow-lg"
                        >
                          <X size={12} />
                        </button>
                      </div>
                      
                      <div className="flex items-center gap-2 mb-2">
                        <GripVertical size={14} className="text-slate-500" />
                        <span className="text-xs font-semibold text-slate-400">{item.name}</span>
                      </div>
                      
                      <div className="bg-slate-900/50 rounded-xl p-3 text-sm text-slate-300">
                        元件預覽內容
                      </div>
                    </div>
                  ))}
                </div>

                {/* 输入框 */}
                <div className="bg-[#17212b] px-4 py-3 flex items-center gap-3">
                  <div className="flex-1 h-10 rounded-full bg-[#242f3d] px-4" />
                  <div className="w-10 h-10 rounded-full bg-indigo-500" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 右侧属性面板 */}
      <div className="w-80 bg-slate-900 border-l border-slate-800 flex flex-col">
        <div className="p-5 border-b border-slate-800">
          <h2 className="text-lg font-bold">屬性設定</h2>
          <p className="text-xs text-slate-500 mt-1">選取元件進行編輯</p>
        </div>

        <div className="flex-1 p-4 overflow-y-auto">
          {selectedItem ? (
            <div className="space-y-5">
              <div className="bg-slate-800/50 rounded-xl p-4">
                <label className="text-xs font-semibold text-slate-400 block mb-2">元件名稱</label>
                <input className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm" defaultValue={canvasItems.find(i => i.id === selectedItem)?.name} />
              </div>
              
              <div className="bg-slate-800/50 rounded-xl p-4 space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-2">位置 X</label>
                  <input type="number" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-2">位置 Y</label>
                  <input type="number" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>

              <div className="bg-slate-800/50 rounded-xl p-4">
                <label className="text-xs font-semibold text-slate-400 block mb-2">寬度</label>
                <input type="range" min="180" max="400" className="w-full" />
              </div>

              <button className="w-full py-2.5 rounded-xl bg-red-500/10 text-red-400 font-medium text-sm hover:bg-red-500/20">
                刪除元件
              </button>
            </div>
          ) : (
            <div className="text-center text-slate-500 py-12">
              <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-slate-800 flex items-center justify-center">
                <Settings size={20} />
              </div>
              點選畫布上的元件
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-800">
          <button className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-pink-500 text-white font-semibold shadow-lg shadow-indigo-500/20">
            💾 儲存版型
          </button>
        </div>
      </div>

    </div>
  )
}