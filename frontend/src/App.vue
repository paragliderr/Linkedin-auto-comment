<template>
  <div class="app">

    <div class="card main-card">
      <div class="header">
        <h1>LinkedIn Auto Commenter</h1>
        <p class="subtitle">AI-powered comments · Keyword filtering · Two scrapers</p>
      </div>
      <div class="controls">
        <div class="scraper-pill-container">
          <div class="scraper-pill">
            <button
              :class="{ active: selectedScraper === 'playwright' }"
              @click="selectedScraper = 'playwright'"
            >Playwright</button>
            <button
              :class="{ active: selectedScraper === 'selenium' }"
              @click="selectedScraper = 'selenium'"
            >Selenium</button>
          </div>
        </div>

        <div class="field">
          <label>Keywords <span class="hint">(comma-separated, leave empty for all posts)</span></label>
          <input
            v-model="keywordInput"
            placeholder="e.g. AI, hiring, startup"
            @keyup.enter="addKeyword"
          />
          <div class="tags" v-if="keywords.length">
            <span
              class="tag"
              v-for="(kw, i) in keywords"
              :key="i"
            >
              {{ kw }}
              <button @click="removeKeyword(i)">×</button>
            </span>
          </div>
        </div>

       <div class="field">
         <label>Your Goal</label>

         <input
           v-model="userGoal"
           placeholder="e.g. Get internships, network with recruiters, build AI presence"
          />
        </div>


        <div class="field">
          <label>Match Mode</label>
          <div class="toggle">
            <button
              :class="{ active: matchMode === 'any' }"
              @click="matchMode = 'any'"
            >Any keyword</button>
            <button
              :class="{ active: matchMode === 'all' }"
              @click="matchMode = 'all'"
            >All keywords</button>
          </div>
        </div>

        <button
          class="run-btn"
          :disabled="loading"
          @click="runPipeline"
        >
          {{ loading ? "Generating Comments..." : "Generate Comments" }}
        </button>
      </div>

      <div class="status-bar" :class="statusClass">
        <span class="dot" /> {{ status }}
      </div>

      <div class="stats" v-if="posts.length">
        <div class="stat">
          <span class="stat-num">{{ posts.length }}</span>
          <span class="stat-label">Posts matched</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ successCount }}</span>
          <span class="stat-label">Generated</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ errorCount }}</span>
          <span class="stat-label">Errors</span>
        </div>
        <div class="stat">
          <span class="stat-num">{{ selectedCount }}</span>
          <span class="stat-label">Selected</span>
        </div>
      </div>

      <div class="toolbar" v-if="posts.length">
        <div class="toolbar-left">
          <label class="custom-checkbox-wrapper select-all">
            <input
              type="checkbox"
              :checked="allSelected"
              :indeterminate="someSelected && !allSelected"
              @change="toggleSelectAll"
            />
            <span class="checkmark"></span>
            <span>{{ allSelected ? "Deselect All" : "Select All" }}</span>
          </label>
        </div>

        <div class="toolbar-right">
          <select v-model="statusFilter" class="filter-select">
            <option value="all">All Statuses</option>
            <option value="generated">Generated</option>
            <option value="edited">Edited</option>
            <option value="posted">Posted</option>
            <option value="failed">Failed</option>
          </select>

          <select v-model="sortOrder" class="filter-select">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>

          <button
            class="bulk-delete-btn"
            v-if="selectedCount"
            @click="removeSelected"
          >
            Remove ({{ selectedCount }})
          </button>

          <button
           class="post-selected-btn"
           v-if="selectedCount"
           @click="postSelected"
         >
            Post Selected ({{ selectedCount }})
         </button>
        </div>
      </div>

      <div class="cards-wrap" v-if="posts.length">
        <div
          class="post-card"
          v-for="(post, i) in filteredPosts"
          :key="i"
          :class="[post.status, { selected: post.selected }]"
        >
          
          <div class="post-card-header">
            <label class="custom-checkbox-wrapper post-select">
              <input
                type="checkbox"
                v-model="post.selected"
              />
              <span class="checkmark"></span>
              <span class="post-number">Post #{{ sortOrder === 'newest' ? posts.length - i : i + 1 }}</span>
            </label>
            <button class="delete-btn" @click="removePost(i)" title="Remove this post">✕</button>
          </div>

          <div class="post-card-body">

            <div class="post-col">
              <div class="section-header">
                <span class="section-title">Original Post</span>
                <a
                  v-if="post.post_url"
                  :href="post.post_url"
                  target="_blank"
                  class="view-post-btn linkedin-btn"
                >
                  LinkedIn ↗
                </a>
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

      <div class="empty" v-if="!posts.length && !loading">
        Run the pipeline to see results here.
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
const keywordInput     = ref("")
const keywords         = ref([])
const matchMode        = ref("any")
const userGoal         = ref("")
const status           = ref("Ready")
const statusClass      = ref("idle")
const loading          = ref(false)
const inputFocused     = ref(false) 
const posts            = ref([])
const statusFilter     = ref("all")
const sortOrder        = ref("newest")

const successCount  = computed(() => posts.value.filter(p => p.status === "generated").length)
const errorCount    = computed(() => posts.value.filter(p => p.status === "error").length)
const selectedCount = computed(() => posts.value.filter(p => p.selected).length)
const allSelected   = computed(() => posts.value.length > 0 && posts.value.every(p => p.selected))
const someSelected  = computed(() => posts.value.some(p => p.selected))

const filteredPosts = computed(() => {
  let result = [...posts.value]
  if (statusFilter.value !== "all") {
    result = result.filter(post => post.status === statusFilter.value)
  }
  if (sortOrder.value === "newest") {
    result.reverse()
  }
  return result
})

function addKeyword() {
  const raw = keywordInput.value.trim()
  if (!raw) return

  raw.split(",")
    .map(k => k.trim())
    .filter(k => k && !keywords.value.includes(k))
    .forEach(k => keywords.value.push(k))
  keywordInput.value = ""
}

function removeKeyword(i) {
  keywords.value.splice(i, 1)
}

function toggleSelectAll() {
  const next = !allSelected.value
  posts.value.forEach(p => { p.selected = next })
}

async function removePost(i) {
  const post = filteredPosts.value[i]
  const originalIndex = posts.value.findIndex(p => p === post)
  
  try {
    await api.delete("/comments/post", {
      params: { post_text: post.post_text }
    })
  } catch (err) {
    console.error("Failed to delete from CSV:", err)
  }
  
  if (originalIndex !== -1) {
    posts.value.splice(originalIndex, 1)
  }
}

async function removeSelected() {
  const toRemove = posts.value.filter(p => p.selected)
  for (const post of toRemove) {
    try {
      await api.delete("/comments/post", {
        params: { post_text: post.post_text }
      })
    } catch (err) {
      console.error("Failed to delete from CSV:", err)
    }
  }
  posts.value = posts.value.filter(p => !p.selected)
}

async function postSelected() {
  const selectedPosts = posts.value.filter(post => post.selected)
  if (!selectedPosts.length) return

  if (!confirm(`Post ${selectedPosts.length} selected comments to LinkedIn?`)) {
    return
  }

  for (const post of selectedPosts) {
    try {
      const response = await api.post("/comments/post-to-linkedin", {
        post_url: post.post_url,
        comment_text: post.edited_comment
      })

      if (response.data.success) {
        post.posted = true
        post.status = "posted"
      } else {
        post.status = "failed"
      }
    } catch (err) {
      console.error(err)
      post.status = "failed"
    }
  }
  alert("Posting completed")
}

async function runPipeline() {
  if (keywordInput.value.trim()) addKeyword()

  loading.value     = true
  status.value      = `Running ${selectedScraper.value} scraper...`
  statusClass.value = "running"
  posts.value       = []

  try {
    const params = {
      scraper_type: selectedScraper.value,
      match_mode: matchMode.value,
      goal: userGoal.value
    }
    keywords.value.forEach(kw => {
      params["keywords"] = params["keywords"]
        ? [...[params["keywords"]].flat(), kw]
        : kw
    })

    await api.post("/comments/run", null, { params })
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

    status.value = `Done — ${posts.value.length} posts processed`
    statusClass.value = "done"

  } catch (err) {
    console.error(err)
    status.value = "Pipeline failed — check console"
    statusClass.value = "error"
  } finally {
    loading.value = false
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

onMounted(() => {
  loadComments()
})
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
  background: #111111;
  border: 1px solid #3a3a3a;
  border-radius: 16px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.95), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.header {
  padding: 40px 36px 24px;
  border-bottom: 1px solid #1e1e1e;
  text-align: center;
}
.header h1 { font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; letter-spacing: -0.02em;}
.header p.subtitle { color: #a3a3a3; font-size: 0.95rem; font-weight: 500; }

.controls { padding: 36px 36px; display: flex; flex-direction: column; align-items: center; gap: 32px; border-bottom: 1px solid #1e1e1e; }

.scraper-pill-container { display: flex; justify-content: center; width: 100%; }
.scraper-pill { display: inline-flex; background: #080808; border: 1px solid #2a2a2a; border-radius: 40px; padding: 4px; }
.scraper-pill button { background: transparent; border: none; color: #777; font-size: 0.85rem; font-weight: 600; padding: 10px 24px; border-radius: 30px; cursor: pointer; transition: all 0.2s ease; }
.scraper-pill button.active { background: #262626; color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.5); }

.super-field { width: 100%; max-width: 720px; text-align: center; }
.super-field label { display: block; font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; margin-bottom: 10px; }
.super-field label .hint { text-transform: none; letter-spacing: 0; color: #555; font-weight: 400; }

.super-input { display: flex; align-items: center; background: #0d0d0d; border: 1px solid #333; border-radius: 12px; padding: 6px 6px 6px 14px; transition: all 0.2s ease; min-height: 54px; }
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

/* Custom Checkbox UI */
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

.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 36px; border-bottom: 1px solid #1e1e1e; background: rgba(17, 17, 17, 0.95); backdrop-filter: blur(8px); position: sticky; top: 0; z-index: 10; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 16px;}
.filter-select { appearance: none; background: #161616; border: 1px solid #2a2a2a; border-radius: 6px; padding: 8px 32px 8px 14px; font-size: 0.85rem; max-width: 150px; color: #ddd; background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e"); background-repeat: no-repeat; background-position: right 12px center; background-size: 14px; }
.select-all { font-size: 0.85rem; color: #aaa; font-weight: 500; }
.bulk-delete-btn, .post-selected-btn { border-radius: 6px; padding: 8px 16px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all .2s;}
.bulk-delete-btn { background: #1f1111; border: 1px solid #3a1c1c; color: #e07f7f; }
.bulk-delete-btn:hover { background: #2a1515; border-color: #e05c5c; color: #ff8c8c; }

.post-selected-btn { background: #0a192f; border: 1px solid #172a45; color: #64b5f6; }
.post-selected-btn:hover { background: #112240; border-color: #64b5f6; box-shadow: 0 4px 16px rgba(100, 181, 246, 0.3);}

/* Post cards */
.cards-wrap { display: flex; flex-direction: column; gap: 32px; padding: 32px 36px 40px; background: #0a0a0a; }

.post-card {
  background: linear-gradient(180deg, #161616, #111111);
  border: 1px solid #222;
  border-radius: 12px;
  overflow: hidden;
  transition: all .3s ease;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
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

.post-card-header { display: flex; justify-content: space-between; align-items: center; background: #1a1a1a; padding: 16px 24px; border-bottom: 1px solid #222; transition: background .2s ease; }
.post-select { display: flex; align-items: center; gap: 14px; cursor: pointer; user-select: none;}

.post-number { font-size: 1.15rem; color: #ffffff; font-weight: 800; letter-spacing: 0.02em;}

.delete-btn { background: none; border: none; color: #555; cursor: pointer; font-size: 1.2rem; transition: color .15s;}
.delete-btn:hover { color: #e05c5c; }

.post-card-body { display: flex; flex-direction: column; gap: 0; padding: 0;}
.post-col { padding: 24px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;}
.section-title { display: block; font-size: 0.9rem; color: #999; text-transform: uppercase; letter-spacing: .08em; font-weight: 700;}

/* Pink Header Title */
.text-pink { color: #ec4899 !important; }

/* Expand/Collapse Toggle Button */
.expand-toggle-btn {
  display: flex; align-items: center; justify-content: center; gap: 12px; width: 100%; background: #1a1a1a;
  border: none; border-top: 1px solid #222; border-bottom: 1px solid #222; color: #aaa;
  padding: 12px 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: background 0.2s, color 0.2s;
}
.expand-toggle-btn:hover { background: #222; color: #fff; }

/* Horizontal Top Glow for AI Workspace */
.comment-workspace { 
  background: #0a0a0a; 
  padding: 24px;
  /* Top border only, no side border */
  border-top: 1px solid rgba(236, 72, 153, 0.4);
  /* Inset shadow constrained to the top vertically */
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
.comment-workspace :deep(input) { 
  background: #000000; 
  border: 1px solid #333; 
  color: #ffffff !important; 
  border-radius: 8px; 
  padding: 16px; 
  font-size: 1.15rem; 
  font-weight: 700; 
  line-height: 1.6;
  width: 100%;
}
.comment-workspace :deep(textarea:focus),
.comment-workspace :deep(input:focus) { border-color: #ec4899; outline: none; box-shadow: 0 0 0 2px rgba(236,72,153,0.2);}


.comment-workspace :deep(button) {
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
}

/* AI Assistant Button Override */
.comment-workspace :deep(button:nth-of-type(1)) {
  background: rgba(168, 85, 247, 0.1) !important;
  border: 1px solid #a855f7 !important; 
  color: #d8b4fe !important;
}
.comment-workspace :deep(button:nth-of-type(1):hover) {
  background: rgba(168, 85, 247, 0.25) !important;
  box-shadow: 0 4px 16px rgba(168, 85, 247, 0.3) !important;
}

/* Individual Post Comment Button Override (Dark Blue) */
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

.empty { padding: 80px 36px; text-align: center; color: #666; font-size: 1rem; }

@media (max-width: 760px) {
  .toolbar { flex-direction: column; align-items: flex-start; }
  .toolbar-left, .toolbar-right { width: 100%; flex-wrap: wrap; }
  .super-input { flex-direction: column; align-items: flex-start; gap: 12px; }
  .inline-match-mode { width: 100%; padding-top: 12px; border-top: 1px solid #333;}
  .inline-match-mode .divider { display: none; }
}
</style>