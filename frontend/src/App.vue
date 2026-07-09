<template>
  <div class="app">
    <div class="card main-card">

      <div class="header">
        <button class="settings-btn" @click="openSettings">⚙ Settings</button>
        <h1>LinkedIn Auto Commenter</h1>
        <p class="subtitle">AI-powered comments · Keyword filtering · Two scrapers</p>
      </div>

      <div class="controls">
        <div class="toggles-group">
          <div class="scraper-pill-container">
            <div class="scraper-pill">
              <button :class="{ active: selectedScraper === 'playwright' }" @click="selectedScraper = 'playwright'">Playwright</button>
              <button :class="{ active: selectedScraper === 'selenium' }" @click="selectedScraper = 'selenium'">Selenium</button>
            </div>
          </div>

          <div class="session-toggle-container">
            <div class="session-toggle">
              <button :class="{ active: sessionType === 'current' }" @click="selectCurrentSession" title="Use saved session">
                <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span class="toggle-text">Current Session</span>
              </button>
              <button :class="{ active: sessionType === 'new' }" @click="startNewSession" title="Start new login session">
                <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle>
                  <line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
                <span class="toggle-text">New Session</span>
              </button>
            </div>
            <div class="session-hint" :class="sessionHintClass" v-if="sessionHintText">{{ sessionHintText }}</div>
          </div>
        </div>

        <div class="field super-field">
          <label>Target Keywords <span class="hint">(Press Enter to add tags)</span></label>
          <div class="super-input" :class="{ 'is-focused': inputFocused }">
            <div class="tags-and-input">
              <span class="tag" v-for="(kw, i) in keywords" :key="i">
                {{ kw }} <button @click="removeKeyword(i)">✕</button>
              </span>
              <input v-model="keywordInput" placeholder="Type keywords..." @keyup.enter="addKeyword" @focus="inputFocused = true" @blur="inputFocused = false" />
            </div>
            <div class="inline-match-mode" v-if="keywords.length > 0 || keywordInput.length > 0">
              <div class="divider"></div>
              <div class="mini-toggle">
                <button :class="{ active: matchMode === 'any' }" @click="matchMode = 'any'">Any keyword</button>
                <button :class="{ active: matchMode === 'all' }" @click="matchMode = 'all'">All keywords</button>
              </div>
            </div>
          </div>
        </div>

        <div class="field super-field">
          <label>Your Goal <span class="hint">(personalizes comments)</span></label>
          <div class="super-input">
            <input v-model="userGoal" placeholder="e.g. Get internships, connect with recruiters..." />
          </div>
        </div>

        <button class="run-btn" :disabled="loading" @click="runPipeline">
          {{ loading ? "Generating..." : "Generate Comments" }}
        </button>
      </div>

      <div class="status-bar" :class="statusClass"><span class="dot" /> {{ status }}</div>

      <div class="stats" v-if="posts.length">
        <div class="stat"><span class="stat-num">{{ posts.length }}</span><span class="stat-label">Matched</span></div>
        <div class="stat"><span class="stat-num">{{ successCount }}</span><span class="stat-label">Generated</span></div>
        <div class="stat"><span class="stat-num">{{ errorCount }}</span><span class="stat-label">Errors</span></div>
        <div class="stat"><span class="stat-num">{{ selectedCount }}</span><span class="stat-label">Selected</span></div>
      </div>

      <div class="toolbar" v-if="posts.length">
        <label class="custom-checkbox-wrapper select-all">
          <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
          <span class="checkmark"></span>
          <span>{{ allSelected ? "Deselect All" : "Select All" }}</span>
        </label>
        <div class="toolbar-right">
          <select v-model="statusFilter" class="filter-select">
            <option value="all">All</option><option value="generated">Generated</option><option value="edited">Edited</option><option value="posted">Posted</option><option value="failed">Failed</option>
          </select>
          <select v-model="sortOrder" class="filter-select">
            <option value="newest">Newest</option><option value="oldest">Oldest</option>
          </select>
          <button class="bulk-delete-btn" v-if="selectedCount" @click="removeSelected">Remove ({{ selectedCount }})</button>
          <button class="post-selected-btn" v-if="selectedCount" @click="postSelected">Post Selected ({{ selectedCount }})</button>
        </div>
      </div>

      <div class="cards-wrap" v-if="posts.length">
        <div class="post-card" v-for="(post, i) in filteredPosts" :key="i" :class="[post.status, { selected: post.selected }]">
          <div class="post-card-header">
            <label class="custom-checkbox-wrapper post-select">
              <input type="checkbox" v-model="post.selected" />
              <span class="checkmark"></span>
              <span class="post-number">Post #{{ sortOrder === 'newest' ? posts.length - i : i + 1 }}</span>
            </label>
            <button class="delete-btn" @click="removePost(i)">✕</button>
          </div>
          <div class="post-card-body">
            <div class="post-col">
              <div class="section-header">
                <span class="section-title">Original Post</span>
                <a v-if="post.post_url" :href="post.post_url" target="_blank" class="view-post-btn linkedin-btn">LinkedIn ↗</a>
              </div>
              <div class="post-content">{{ post.post_text }}</div>
            </div>
            <button class="expand-toggle-btn" @click="post.isExpanded = !post.isExpanded">
              {{ post.isExpanded ? 'Hide comment ▲' : 'View comment ▼' }}
              <span class="badge" :class="post.status" v-if="!post.isExpanded">{{ post.status }}</span>
            </button>
            <div class="comment-workspace" v-show="post.isExpanded">
              <div class="section-header">
                <span class="section-title text-pink">AI Generated Comment</span>
              </div>
              <CommentEditor :post="post" />
            </div>
          </div>
        </div>
      </div>

      <div class="empty" v-if="!posts.length && !loading">Run the pipeline to see results here.</div>
    </div>

    <div v-if="showSettings" class="settings-overlay" @click.self="showSettings = false">
      <div class="settings-modal">
        <div class="settings-header">
          <h2>Settings</h2>
          <button class="close-btn" @click="showSettings = false">✕</button>
        </div>
        
        <div class="settings-body">
          <div class="field">
            <label>API Key</label>
            <input v-model="settings.api_key" type="password" placeholder="Enter key" />
          </div>
          <div class="field">
            <label>Base URL</label>
            <input v-model="settings.base_url" placeholder="https://..." />
          </div>
          <div class="field">
            <label>Model</label>
            <input v-model="settings.model" placeholder="Model name" />
          </div>

          <div class="field">
            <label>Comment Source</label>
            <div class="mini-toggle" style="display:inline-flex; margin-top:4px;">
              <button :class="{ active: settings.comment_source === 'api' }" @click="settings.comment_source = 'api'" type="button">API</button>
              <button :class="{ active: settings.comment_source === 'browser' }" @click="settings.comment_source = 'browser'" type="button">Browser Chatbot</button>
            </div>
          </div>

          <template v-if="settings.comment_source === 'browser'">
            <div class="field">
              <label>Chatbot URL</label>
              <input v-model="settings.browser_ai_url" placeholder="https://chat.openai.com/" />
            </div>
            <div class="field">
              <label>Input Box Selector</label>
              <input v-model="settings.browser_ai_input_css" placeholder="#prompt-textarea" />
            </div>
            <div class="field">
              <label>Send Button Selector</label>
              <input v-model="settings.browser_ai_send_css" placeholder="button[data-testid='send-button']" />
            </div>
            <div class="field">
              <label>Reply Selector</label>
              <input v-model="settings.browser_ai_reply_css" placeholder="div[data-message-author-role='assistant']" />
            </div>
            
            <button class="secondary-btn" style="width: 100%; margin-top: 8px; text-align: center;" type="button" @click="startBrowserAiSession" :disabled="startingBrowserAi">
              {{ startingBrowserAi ? "Opening…" : "Start Browser Session" }}
            </button>
            
            <div class="session-hint" :class="browserAiHintClass" v-if="browserAiHint">{{ browserAiHint }}</div>
          </template>

        </div>

        <div class="settings-footer">
          <button class="secondary-btn" @click="showSettings = false">Cancel</button>
          <button class="primary-btn" :disabled="savingSettings" @click="saveSettings">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import api from "./services/api"
import CommentEditor from "./components/CommentEditor/CommentEditor.vue"
import { getHistory } from "./services/historyService"

const selectedScraper = ref("selenium")
const sessionType      = ref("current") 
const keywordInput     = ref("")
const keywords         = ref([])
const matchMode        = ref("any")
const status           = ref("Ready")
const statusClass      = ref("idle")
const loading          = ref(false)
const inputFocused     = ref(false) 
const posts            = ref([])
const statusFilter     = ref("all")
const sortOrder        = ref("newest")
const userGoal         = ref("")

const showSettings     = ref(false)
const savingSettings   = ref(false)

// UPDATED: Added Browser AI fields to settings ref
const settings = ref({ 
  api_key: "", 
  base_url: "", 
  model: "",
  comment_source: "api",
  browser_ai_url: "",
  browser_ai_input_css: "",
  browser_ai_send_css: "",
  browser_ai_reply_css: ""
})

// NEW: Browser AI specific refs
const startingBrowserAi = ref(false)
const browserAiHint = ref("")
const browserAiHintClass = ref("")

const sessionExists    = ref(false)
const checkingSession  = ref(false)
const startingSession  = ref(false)

const successCount  = computed(() => posts.value.filter(p => p.status === "generated").length)
const errorCount    = computed(() => posts.value.filter(p => p.status === "error").length)
const selectedCount = computed(() => posts.value.filter(p => p.selected).length)
const allSelected   = computed(() => posts.value.length > 0 && posts.value.every(p => p.selected))
const someSelected  = computed(() => posts.value.some(p => p.selected))

const filteredPosts = computed(() => {
  let result = [...posts.value]
  if (statusFilter.value !== "all") result = result.filter(post => post.status === statusFilter.value)
  if (sortOrder.value === "newest") result.reverse()
  return result
})

const sessionHintText = computed(() => {
  if (checkingSession.value) return "Checking session…"
  if (sessionType.value === "new" && startingSession.value) return "Log in in the browser window…"
  if (sessionExists.value) return "✓ Session ready"
  if (sessionType.value === "current") return "No saved session — click New Session"
  return ""
})

const sessionHintClass = computed(() => {
  if (checkingSession.value) return "checking"
  if (sessionType.value === "new" && startingSession.value) return "info"
  if (sessionExists.value) return "success"
  return "warning"
})

const canRunPipeline = computed(() => {
  if (sessionType.value === 'new') return !startingSession.value
  return sessionExists.value
})

async function checkSession() {
  checkingSession.value = true
  try {
    const res = await api.get("/auth/check-session")
    sessionExists.value = !!res.data?.exists
  } catch (err) {
    sessionExists.value = false
  } finally {
    checkingSession.value = false
  }
}

function selectCurrentSession() { sessionType.value = "current"; checkSession(); }

async function startNewSession() {
  sessionType.value = "new"; startingSession.value = true;
  try {
    await api.post("/auth/login")
    for (let i = 0; i < 60; i++) {
      await new Promise(r => setTimeout(r, 5000))
      const res = await api.get("/auth/check-session")
      if (res.data?.exists) { sessionExists.value = true; startingSession.value = false; break; }
    }
  } catch (e) { console.error(e); } finally { startingSession.value = false; }
}

// NEW: Function to start Browser AI Session
async function startBrowserAiSession() {
  startingBrowserAi.value = true
  browserAiHint.value = "Opening browser…"
  browserAiHintClass.value = "info"
  try {
    const res = await api.post("/browser-ai/start", {
      url: settings.value.browser_ai_url,
      input_css: settings.value.browser_ai_input_css,
      send_css: settings.value.browser_ai_send_css,
      reply_css: settings.value.browser_ai_reply_css
    })
    if (res.data.status === "needs_manual_login") {
      browserAiHint.value = "Log in in the opened window, then click again to save."
      browserAiHintClass.value = "warning"
    } else {
      browserAiHint.value = "✓ Session active"
      browserAiHintClass.value = "success"
    }
  } catch (err) {
    console.error(err)
    browserAiHint.value = "Failed to open session — check backend"
    browserAiHintClass.value = "error"
  } finally {
    startingBrowserAi.value = false
  }
}

function addKeyword() {
  const raw = keywordInput.value.trim()
  if (!raw) return
  raw.split(",").map(k => k.trim()).filter(k => k && !keywords.value.includes(k)).forEach(k => keywords.value.push(k))
  keywordInput.value = ""
}

function removeKeyword(i) { keywords.value.splice(i, 1) }

function toggleSelectAll() {
  const next = !allSelected.value
  posts.value.forEach(p => { p.selected = next })
}

async function runPipeline() {
  if (keywordInput.value.trim()) addKeyword()
  if (!canRunPipeline.value) { status.value = "Set up a session first"; statusClass.value = "error"; return; }

  loading.value = true; status.value = `Running ${selectedScraper.value}…`; statusClass.value = "running"
  try {
    const prevCount = (await getHistory()).length
    const params = { scraper_type: selectedScraper.value, session_type: sessionType.value, match_mode: matchMode.value, goal: userGoal.value, keywords: keywords.value }
    const response = await api.post("/comments/run", null, { params })
    const jobId = response.data
    let jobStatus = "running"
    while (jobStatus === "running") {
      await new Promise(r => setTimeout(r, 2000))
      jobStatus = (await api.get(`/comments/run/status/${jobId}`)).data.status
    }
    const history = await getHistory()
    posts.value = history.map(p => ({ ...p, selected: false, isExpanded: false }))
    status.value = `Done — ${history.length - prevCount} new posts`
  } catch (e) { console.error(e); status.value = "Failed"; statusClass.value = "error" } finally { loading.value = false }
}

async function openSettings() { 
  showSettings.value = true;
  try {
    const response = await api.get("/settings")
    settings.value = { ...settings.value, ...response.data }
    // Ensure default fallback if backend is empty
    if (!settings.value.comment_source) settings.value.comment_source = 'api'
  } catch (error) {
    console.error("Failed to load settings:", error)
  }
}

async function saveSettings() { 
  savingSettings.value = true; 
  try {
    await api.post("/settings", settings.value); 
    status.value = "Settings saved";
    statusClass.value = "done";
  } catch (e) {
    console.error("Save failed", e);
  } finally {
    showSettings.value = false; 
    savingSettings.value = false; 
  }
}

async function loadComments() {
  const history = await getHistory()
  posts.value = history.map(post => ({
    ...post,
    editing: false,
    edited: post.status === "edited",
    edited_comment: post.generated_comment,
    selected: false,
    posted: post.status === "posted",
    isExpanded: false 
  }))
}

onMounted(() => { loadComments(); checkSession(); })
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }

.app {
  min-height: 100vh;
  background: #000000;
  display: flex;
  justify-content: center;
  padding: 40px 16px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #e0e0e0;
}

.main-card {
  width: 100%;
  max-width: 1160px;
  background: #0d0d0d;
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 16px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.95), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.header {
  position: relative;
  padding: 40px 36px 24px;
  border-bottom: 1px solid #1e1e1e;
  text-align: center;
}

.header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.header .subtitle {
  color: #a3a3a3;
  font-size: 0.95rem;
  font-weight: 500;
}

.settings-btn {
  position: absolute;
  top: 32px;
  right: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #111111;
  color: #e0e0e0;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.settings-btn:hover {
  background: #1b1b1b;
  border-color: #4caf7d;
  color: #ffffff;
  box-shadow: 0 0 18px rgba(76, 175, 125, 0.15);
}

.controls { padding: 36px 36px; display: flex; flex-direction: column; align-items: center; gap: 32px; border-bottom: 1px solid #1e1e1e; }

.toggles-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.scraper-pill-container { display: flex; justify-content: center; width: 100%; }
.scraper-pill { display: inline-flex; background: #080808; border: 1px solid #2a2a2a; border-radius: 40px; padding: 4px; }
.scraper-pill button { background: transparent; border: none; color: #777; font-size: 0.85rem; font-weight: 600; padding: 10px 24px; border-radius: 30px; cursor: pointer; transition: all 0.2s ease; }
.scraper-pill button.active { background: #262626; color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }

.session-toggle-container { display: flex; flex-direction: column; align-items: center; gap: 10px; width: 100%; }

.session-toggle { 
  display: inline-flex; 
  background: #111111; 
  border: 1px solid #222; 
  border-radius: 40px; 
  padding: 4px; 
  gap: 4px;
}
.session-toggle button { 
  display: flex; 
  align-items: center; 
  background: transparent; 
  border: none; 
  color: #666; 
  font-size: 0.85rem; 
  border-radius: 30px; 
  padding: 8px 12px; 
  cursor: pointer; 
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
}
.session-toggle button.active { 
  background: #e0e0e0; 
  color: #111; 
  box-shadow: 0 4px 12px rgba(255,255,255,0.1); 
}
.session-toggle button.disabled {
  opacity: 0.5;
}
.session-toggle .toggle-text { 
  max-width: 0; 
  opacity: 0; 
  overflow: hidden; 
  white-space: nowrap; 
  font-weight: 700; 
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
  margin-left: 0; 
}
.session-toggle button.active .toggle-text { 
  max-width: 160px; 
  opacity: 1; 
  margin-left: 8px; 
}

.session-hint {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  text-align: center;
  max-width: 480px;
}
.session-hint.warning { background: rgba(240, 192, 64, 0.1); color: #f0c040; border: 1px solid rgba(240, 192, 64, 0.3); }
.session-hint.success { background: rgba(76, 175, 125, 0.1); color: #4caf7d; border: 1px solid rgba(76, 175, 125, 0.3); }
.session-hint.info { background: rgba(100, 181, 246, 0.1); color: #64b5f6; border: 1px solid rgba(100, 181, 246, 0.3); }
.session-hint.checking { color: #777; }

.super-field { width: 100%; max-width: 720px; text-align: center; }
.super-field label { display: block; font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; margin-bottom: 10px; }
.super-field label .hint { text-transform: none; letter-spacing: 0; color: #555; font-weight: 400; }

.super-input { display: flex; align-items: center; background: #080808; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 6px 6px 6px 14px; transition: all 0.2s ease; min-height: 54px; }
.super-input.is-focused { border-color: #4caf7d; box-shadow: 0 0 0 3px rgba(76, 175, 125, 0.15); }

.tags-and-input { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; flex: 1; }
.tag { display: flex; align-items: center; gap: 8px; background: #1a1a1a; border: 1px solid #333; border-radius: 6px; padding: 6px 12px; font-size: 0.85rem; color: #ddd; }
.tag button { background: none; border: none; color: #888; cursor: pointer; font-size: 1rem; line-height: 1; padding: 0; }
.tag button:hover { color: #e05c5c; }

.super-input input { background: transparent; border: none; outline: none; color: #e0e0e0; font-size: 0.95rem; flex: 1; min-width: 180px; padding: 6px 0; }
.super-input input::placeholder { color: #555; }

.inline-match-mode { display: flex; align-items: center; height: 100%; }
.inline-match-mode .divider { width: 1px; height: 24px; background: #333; margin: 0 8px; }
.mini-toggle { display: inline-flex; background: #161616; border: 1px solid #333; border-radius: 8px; padding: 3px; }
.mini-toggle button { background: transparent; border: none; color: #888; font-size: 0.75rem; font-weight: 600; padding: 6px 12px; border-radius: 6px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.mini-toggle button.active { background: #333; color: #fff; }

.run-btn { background: #ffffff; color: #000000; border: none; border-radius: 8px; padding: 14px 40px; font-size: 1rem; font-weight: 700; cursor: pointer; transition: all .2s; box-shadow: 0 4px 12px rgba(255,255,255,0.1); }
.run-btn:hover { opacity: .9; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(255,255,255,0.15);}
.run-btn:active { transform: translateY(0); }
.run-btn:disabled { opacity: .5; cursor: not-allowed; transform: none; box-shadow: none;}

.custom-checkbox-wrapper { display: flex; align-items: center; gap: 12px; cursor: pointer; user-select: none; }
.custom-checkbox-wrapper input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark { display: inline-block; width: 20px; height: 20px; background-color: #1a1a1a; border: 2px solid #444; border-radius: 6px; position: relative; transition: all 0.2s ease; }
.custom-checkbox-wrapper:hover input ~ .checkmark { border-color: #666; }
.custom-checkbox-wrapper input:checked ~ .checkmark { background-color: #4caf7d; border-color: #4caf7d; box-shadow: 0 0 8px rgba(76, 175, 125, 0.4); }
.checkmark:after { content: ""; position: absolute; display: none; left: 6px; top: 2px; width: 5px; height: 10px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }
.custom-checkbox-wrapper input:checked ~ .checkmark:after { display: block; }

.status-bar { padding: 14px 36px; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 10px; border-bottom: 1px solid #1a1a1a; color: #777; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #333; flex-shrink: 0;}
.status-bar.running .dot { background: #f0c040; box-shadow: 0 0 12px rgba(240,192,64,0.6); }
.status-bar.running { color: #f0c040; }
.status-bar.done .dot { background: #4caf7d; box-shadow: 0 0 12px rgba(76,175,125,0.6); }
.status-bar.done { color: #4caf7d; }
.status-bar.error .dot { background: #e05c5c; box-shadow: 0 0 12px rgba(224,92,92,0.6); }
.status-bar.error { color: #e05c5c; }

.stats { display: flex; gap: 0; border-bottom: 1px solid #1a1a1a; }
.stat { flex: 1; padding: 24px 36px; display: flex; flex-direction: column; gap: 6px; align-items: center; text-align: center; border-right: 1px solid #1a1a1a; }
.stat:last-child { border-right: none; }
.stat-num { font-size: 1.8rem; font-weight: 700; color: #fff; line-height: 1; }
.stat-label { font-size: 0.75rem; color: #777; text-transform: uppercase; letter-spacing: .05em; font-weight: 600;}

.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 36px; border-bottom: 1px solid #1e1e1e; background: rgba(13, 13, 13, 0.95); backdrop-filter: blur(8px); position: sticky; top: 0; z-index: 10; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 16px;}
.filter-select { appearance: none; background: #161616; border: 1px solid #2a2a2a; border-radius: 6px; padding: 8px 32px 8px 14px; font-size: 0.85rem; max-width: 150px; color: #ddd; background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e"); background-repeat: no-repeat; background-position: right 12px center; background-size: 14px; }
.select-all { font-size: 0.85rem; color: #aaa; font-weight: 500; }
.bulk-delete-btn, .post-selected-btn { border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all .2s;}
.bulk-delete-btn { background: #1f1111; border: 1px solid #3a1c1c; color: #e07f7f; }
.bulk-delete-btn:hover { background: #2a1515; border-color: #e05c5c; color: #ff8c8c; }

.post-selected-btn { background: #0a192f; border: 1px solid #172a45; color: #64b5f6; }
.post-selected-btn:hover { background: #112240; border-color: #64b5f6; box-shadow: 0 4px 16px rgba(100, 181, 246, 0.3);}

.cards-wrap { display: flex; flex-direction: column; gap: 32px; padding: 32px 36px 40px; background: #000000; }

.post-card {
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.08); 
  border-radius: 12px;
  overflow: hidden;
  transition: all .3s ease;
  position: relative;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.post-card.selected { 
  border-color: #355a44; 
  box-shadow: -4px 0 32px -6px rgba(76, 175, 125, 0.5), 0 8px 24px rgba(0,0,0,0.8);
}
.post-card.selected .post-card-header { background: rgba(76, 175, 125, 0.05); }

.post-card.generated { box-shadow: -3px 0 24px -4px rgba(76, 175, 125, 0.4); border-left: 1px solid #4caf7d; }
.post-card.edited { box-shadow: -3px 0 24px -4px rgba(240, 192, 64, 0.4); border-left: 1px solid #f0c040; }
.post-card.posted { box-shadow: -3px 0 24px -4px rgba(77, 163, 255, 0.4); border-left: 1px solid #4da3ff; }
.post-card.error, .post-card.failed { box-shadow: -3px 0 24px -4px rgba(224, 92, 92, 0.4); border-left: 1px solid #e05c5c; }

.post-card-header { display: flex; justify-content: space-between; align-items: center; background: #161616; padding: 16px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background .2s ease; }
.post-select { display: flex; align-items: center; gap: 14px; cursor: pointer; user-select: none;}

.post-number { font-size: 1.15rem; color: #ffffff; font-weight: 800; letter-spacing: 0.02em;}

.delete-btn { background: none; border: none; color: #555; cursor: pointer; font-size: 1.2rem; transition: color .15s;}
.delete-btn:hover { color: #e05c5c; }

.post-card-body { display: flex; flex-direction: column; gap: 0; padding: 0;}
.post-col { padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;}
.section-title { display: block; font-size: 0.9rem; color: #999; text-transform: uppercase; letter-spacing: .08em; font-weight: 700;}

.text-pink { color: #ec4899 !important; }

.expand-toggle-btn {
  display: flex; align-items: center; justify-content: center; gap: 12px; width: 100%; background: #111111;
  border: none; border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); color: #aaa;
  padding: 12px 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: background 0.2s, color 0.2s;
}
.expand-toggle-btn:hover { background: #1a1a1a; color: #fff; }

.comment-workspace { 
  background: #050505; 
  padding: 24px;
  border-top: 1px solid rgba(236, 72, 153, 0.4);
  box-shadow: inset 0 20px 30px -20px rgba(236, 72, 153, 0.25);
}

.badge { padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; white-space: nowrap;}
.badge.generated { background: #122b1f; color: #4caf7d; border: 1px solid #1a422f;}
.badge.edited { background: #2e260c; color: #f0c040; border: 1px solid #4a3e14;}
.badge.posted { background: #0d1a2a; color: #4da3ff; border: 1px solid #183353;}
.badge.error, .badge.failed { background: #2e1515; color: #e05c5c; border: 1px solid #4a2121;}

.post-content { 
  font-size: 1.05rem; 
  line-height: 1.6; 
  color: #dddddd; 
  font-weight: 400; 
  white-space: pre-wrap; 
  word-break: break-word; 
  max-height: 500px; 
  overflow-y: auto; 
  padding-right: 8px;
}
.post-content::-webkit-scrollbar { width: 6px; }
.post-content::-webkit-scrollbar-thumb { background: #444; border-radius: 3px; }

.linkedin-btn { 
  padding: 6px 16px; border-radius: 6px; background: rgba(40, 103, 178, 0.1); 
  border: 1px solid rgba(40, 103, 178, 0.4); color: #70b5f9; text-decoration: none; 
  font-size: 0.85rem; font-weight: 600; transition: all .2s;
}
.linkedin-btn:hover { background: rgba(40, 103, 178, 0.2); border-color: #70b5f9;}

.comment-workspace :deep(textarea),
.comment-workspace :deep(input),
.comment-workspace :deep(.editor-content),
.comment-workspace :deep([contenteditable]) { 
  background: #050505 !important; 
  border: 1px solid rgba(255, 255, 255, 0.1) !important; 
  color: #ffffff !important; 
  border-radius: 8px !important; 
  padding: 16px !important; 
  font-size: 1.15rem !important; 
  font-weight: 700 !important; 
  line-height: 1.6 !important;
  width: 100% !important;
}
.comment-workspace :deep(textarea:focus),
.comment-workspace :deep(input:focus),
.comment-workspace :deep([contenteditable]:focus) { 
  border-color: #ec4899 !important; 
  outline: none !important; 
  box-shadow: 0 0 0 2px rgba(236,72,153,0.2) !important;
}

.comment-workspace :deep(button) {
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

.comment-workspace :deep(button:nth-of-type(1)) {
  background: rgba(168, 85, 247, 0.1) !important;
  border: 1px solid #a855f7 !important; 
  color: #d8b4fe !important;
}
.comment-workspace :deep(button:nth-of-type(1):hover) {
  background: rgba(168, 85, 247, 0.25) !important;
  box-shadow: 0 4px 16px rgba(168, 85, 247, 0.3) !important;
}

.comment-workspace :deep(button:nth-of-type(2)) {
  background: #0a192f !important;
  border: 1px solid #172a45 !important;
  color: #64b5f6 !important;
}
.comment-workspace :deep(button:nth-of-type(2):hover) {
  background: #112240 !important;
  border-color: #64b5f6 !important;
  box-shadow: 0 4px 16px rgba(100, 181, 246, 0.3) !important;
}

.comment-workspace :deep(.edited),
.comment-workspace :deep(.badge.edited),
.comment-workspace :deep(.editor-badge) {
  background: rgba(245, 158, 11, 0.15) !important;
  color: #fbbf24 !important;
  border: 1px solid rgba(245, 158, 11, 0.4) !important;
  padding: 4px 12px !important;
  border-radius: 6px !important;
  font-weight: 700 !important;
  font-size: 0.75rem !important;
  text-transform: uppercase !important;
}

.empty { padding: 80px 36px; text-align: center; color: #666; font-size: 1rem; }

@media (max-width: 760px) {
  .toolbar { flex-direction: column; align-items: flex-start; }
  .toolbar-left, .toolbar-right { width: 100%; flex-wrap: wrap; }
  .super-input { flex-direction: column; align-items: flex-start; gap: 12px; }
  .inline-match-mode { width: 100%; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1);}
  .inline-match-mode .divider { display: none; }
}

/* ================= SETTINGS MODAL ================= */

.settings-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(6px);
}

.settings-modal {
  width: 100%;
  max-width: 500px;
  background: #0d0d0d;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 18px;
  box-shadow: 0 25px 80px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.05);
  overflow: hidden;
  max-height: 90vh; 
  display: flex;
  flex-direction: column;
}

.settings-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:22px 28px;
  border-bottom:1px solid #1e1e1e;
}

.settings-header h2{
  font-size:1.35rem;
  color:white;
}

.close-btn{
  background:none;
  border:none;
  color:#888;
  font-size:1.4rem;
  cursor:pointer;
  transition:.2s;
}

.close-btn:hover{
  color:white;
}

.settings-body{
  padding:28px;
  display:flex;
  flex-direction:column;
  gap:22px;
  overflow-y: auto; 
}

.settings-body .field{
  display:flex;
  flex-direction:column;
  gap:8px;
}

.settings-body label{
  font-size:.8rem;
  color:#888;
  text-transform:uppercase;
  letter-spacing:.08em;
}

.settings-body input{
  background:#080808;
  border:1px solid rgba(255,255,255,.1);
  color:white;
  border-radius:10px;
  padding:14px 16px;
  font-size:.95rem;
  outline:none;
  transition:.2s;
}

.settings-body input:focus{
  border-color:#4caf7d;
  box-shadow:0 0 0 3px rgba(76,175,125,.15);
}

.settings-footer{
  display:flex;
  justify-content:flex-end;
  gap:12px;
  padding:24px 28px;
  border-top:1px solid #1e1e1e;
}

.secondary-btn{
  background:transparent;
  color:#999;
  border:1px solid #333;
  border-radius:10px;
  padding:10px 18px;
  cursor:pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.secondary-btn:hover{
  border-color:#555;
  color:white;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary-btn{
  background:#4caf7d;
  color:white;
  border:none;
  border-radius:10px;
  padding:10px 22px;
  font-weight:600;
  cursor:pointer;
  transition:.2s;
}

.primary-btn:hover{
  background:#5bb987;
}

.primary-btn:disabled{
  opacity: 0.5;
  cursor: not-allowed;
}
</style>