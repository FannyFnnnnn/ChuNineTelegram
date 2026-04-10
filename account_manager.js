// 🔐 多账号会话管理系统
class AccountManager {
    constructor() {
        this.accounts = this.load()
        this.currentAccount = null
    }

    load() {
        try {
            const data = localStorage.getItem('chujiu_bot_accounts')
            return data ? JSON.parse(data) : {}
        } catch(e) {
            return {}
        }
    }

    save() {
        localStorage.setItem('chujiu_bot_accounts', JSON.stringify(this.accounts))
    }

    add(account) {
        const id = account.id || Date.now().toString(36)
        this.accounts[id] = {
            id,
            name: account.name,
            token: account.token,
            groupId: account.groupId,
            admins: account.admins || [],
            config: account.config || {},
            createdAt: new Date().toISOString(),
            lastUsed: new Date().toISOString()
        }
        this.save()
        return id
    }

    get(id) {
        const acc = this.accounts[id]
        if (acc) acc.lastUsed = new Date().toISOString()
        this.save()
        return acc
    }

    list() {
        return Object.values(this.accounts).sort((a,b) => new Date(b.lastUsed) - new Date(a.lastUsed))
    }

    delete(id) {
        delete this.accounts[id]
        this.save()
    }

    exportAll() {
        return btoa(JSON.stringify(this.accounts))
    }

    importAll(encoded) {
        try {
            this.accounts = JSON.parse(atob(encoded))
            this.save()
            return true
        } catch(e) {
            return false
        }
    }
}

// 全局实例
window.Accounts = new AccountManager()

// 账号切换UI组件
function renderAccountSelector() {
    const accounts = Accounts.list()
    
    return `
    <div class="card mb-5">
        <div class="card-header">
            <h3 class="card-title">🔐 帳號管理</h3>
            <button class="btn btn-primary btn-sm" onclick="showAddAccountModal()">+ 新增帳號</button>
        </div>
        
        <div class="account-list">
            ${accounts.length === 0 ? `
                <div class="text-center py-8 text-slate-500">
                    <div class="text-4xl mb-3">🔑</div>
                    <p>尚未儲存任何機器人帳號</p>
                    <button class="btn btn-primary mt-4" onclick="showAddAccountModal()">新增第一個帳號</button>
                </div>
            ` : accounts.map(acc => `
                <div class="account-item ${Accounts.currentAccount === acc.id ? 'active' : ''}" data-id="${acc.id}">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
                            ${acc.name.charAt(0).toUpperCase()}
                        </div>
                        <div class="flex-1">
                            <div class="font-semibold">${acc.name}</div>
                            <div class="text-xs text-slate-500">${acc.groupId} • 最後使用 ${timeAgo(acc.lastUsed)}</div>
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-sm btn-outline" onclick="selectAccount('${acc.id}')">切換</button>
                            <button class="btn btn-sm btn-danger" onclick="deleteAccount('${acc.id}')">刪除</button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="mt-4 pt-4 border-t border-slate-700">
            <div class="flex gap-2">
                <button class="btn btn-outline flex-1" onclick="exportAccounts()">📤 匯出所有帳號</button>
                <button class="btn btn-outline flex-1" onclick="showImportModal()">📥 匯入帳號</button>
            </div>
        </div>
    </div>
    
    <!-- 新增帳號彈窗 -->
    <div id="addAccountModal" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header">
                <h3>新增機器人帳號</h3>
                <button onclick="closeModal('addAccountModal')" class="text-slate-400 hover:text-white">✕</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">帳號名稱</label>
                    <input type="text" class="form-input" id="acc_name" placeholder="例如：初玖主機器人">
                </div>
                <div class="form-group">
                    <label class="form-label">Bot Token</label>
                    <input type="text" class="form-input" id="acc_token" placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ">
                </div>
                <div class="form-group">
                    <label class="form-label">群組 ID</label>
                    <input type="text" class="form-input" id="acc_groupId" placeholder="-1001234567890">
                </div>
                <div class="form-group">
                    <label class="form-label">管理員 ID (每行一個)</label>
                    <textarea class="form-input" rows="3" id="acc_admins"></textarea>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('addAccountModal')">取消</button>
                <button class="btn btn-primary" onclick="saveNewAccount()">儲存帳號</button>
            </div>
        </div>
    </div>
    
    <!-- 匯入彈窗 -->
    <div id="importModal" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header">
                <h3>匯入帳號</h3>
                <button onclick="closeModal('importModal')" class="text-slate-400 hover:text-white">✕</button>
            </div>
            <div class="modal-body">
                <p class="text-sm text-slate-400 mb-4">貼上你從其他裝置匯出的帳號代碼</p>
                <textarea class="form-input" rows="6" id="import_data" placeholder="貼上匯出編碼..."></textarea>
            </div>
            <div class="modal-footer">
                <button class="btn btn-outline" onclick="closeModal('importModal')">取消</button>
                <button class="btn btn-primary" onclick="doImport()">匯入</button>
            </div>
        </div>
    </div>
    `
}

function showAddAccountModal() {
    document.getElementById('addAccountModal').classList.remove('hidden')
}

function showImportModal() {
    document.getElementById('importModal').classList.remove('hidden')
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden')
}

function saveNewAccount() {
    const id = Accounts.add({
        name: document.getElementById('acc_name').value,
        token: document.getElementById('acc_token').value,
        groupId: document.getElementById('acc_groupId').value,
        admins: document.getElementById('acc_admins').value.split('\n').filter(x => x.trim())
    })
    
    selectAccount(id)
    closeModal('addAccountModal')
    refreshUI()
    addLog('success', `✅ 已儲存帳號: ${document.getElementById('acc_name').value}`)
}

function selectAccount(id) {
    Accounts.currentAccount = id
    const acc = Accounts.get(id)
    
    // 自动填充所有配置栏位
    document.getElementById('configToken').value = acc.token
    document.getElementById('configGroupId').value = acc.groupId
    document.getElementById('configAdmins').value = acc.admins.join('\n')
    document.getElementById('configGroupName').value = acc.name
    
    refreshUI()
    addLog('info', `🔄 已切換至帳號: ${acc.name}`)
}

function deleteAccount(id) {
    const name = Accounts.get(id).name
    Accounts.delete(id)
    if (Accounts.currentAccount === id) Accounts.currentAccount = null
    refreshUI()
    addLog('warning', `🗑️ 已刪除帳號: ${name}`)
}

function exportAccounts() {
    const code = Accounts.exportAll()
    navigator.clipboard.writeText(code)
    addLog('success', '✅ 所有帳號已複製到剪貼簿')
    alert('帳號匯出編碼已複製到剪貼簿\n你可以在任何裝置貼上匯入')
}

function doImport() {
    const data = document.getElementById('import_data').value
    if (Accounts.importAll(data)) {
        closeModal('importModal')
        refreshUI()
        addLog('success', `✅ 成功匯入 ${Object.keys(Accounts.accounts).length} 個帳號`)
    } else {
        addLog('error', '❌ 匯入失敗，格式錯誤')
    }
}

function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000)
    if (seconds < 60) return '剛剛'
    if (seconds < 3600) return `${Math.floor(seconds/60)} 分鐘前`
    if (seconds < 86400) return `${Math.floor(seconds/3600)} 小時前`
    return `${Math.floor(seconds/86400)} 天前`
}

function refreshUI() {
    // 重新渲染帳號選擇器
    const container = document.querySelector('[data-account-container]')
    if (container) {
        container.innerHTML = renderAccountSelector()
    }
    
    // 更新狀態欄
    if (Accounts.currentAccount) {
        const acc = Accounts.get(Accounts.currentAccount)
        document.getElementById('statusAccount').textContent = acc.name
    }
}