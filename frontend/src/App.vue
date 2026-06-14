<template>
  <div class="app">

    <div class="card">

      <div class="header">
        <h1>LinkedIn Auto Commenter</h1>
        <p>AI-powered comments · Keyword filtering · Two scrapers</p>
      </div>

      <div class="controls">

        <div class="field">
          <label>Scraper</label>
          <select v-model="selectedScraper">
            <option value="playwright">Playwright</option>
            <option value="selenium">Selenium</option>
          </select>
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
          {{ loading ? "Running..." : "Generate Comments" }}
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
          <span class="stat-label">Comments generated</span>
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
        <label class="select-all">
          <input
            type="checkbox"
            :checked="allSelected"
            :indeterminate="someSelected && !allSelected"
            @change="toggleSelectAll"
          />
          <span>{{ allSelected ? "Deselect all" : "Select all" }}</span>
        </label>

        <select v-model="statusFilter" class="filter-select">
          <option value="all">All</option>
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
          Remove {{ selectedCount }} selected
        </button>
      </div>

      <div class="cards-wrap" v-if="posts.length">
        <div
          class="post-card"
          v-for="(post, i) in filteredPosts"
          :key="i"
          :class="[post.status, { selected: post.selected }]"
        >
          <div class="post-card-select">
            <input
              type="checkbox"
              v-model="post.selected"
            />
            <span class="post-index">#{{ i + 1 }}</span>
          </div>

          <div class="post-card-body">

            <div class="post-col">
              <span class="col-label">Original post</span>
              <div class="post-content">{{ post.post_text }}</div>
              <a
                v-if="post.post_url"
                :href="post.post_url"
                target="_blank"
                class="view-post-btn"
              >
                View on LinkedIn ↗
              </a>
            </div>

            <div class="comment-col">
              <div class="comment-col-head">
                <span class="col-label">Generated comment</span>
                <span class="badge" :class="post.status">{{ post.status }}</span>
              </div>
              <CommentEditor :post="post" />
            </div>

          </div>

          <button class="delete-btn" @click="removePost(i)" title="Remove this post">✕</button>
        </div>
      </div>

      <!-- History removed temporarily -->

      <div class="empty" v-if="!posts.length && !loading">
        Run the pipeline to see results here.
      </div>

    </div>
  </div>
</template>

<script setup>

import { ref, computed,onMounted } from "vue"
import api from "./services/api"

import CommentEditor from "./components/CommentEditor/CommentEditor.vue"
import { getHistory } from "./services/historyService"


const selectedScraper = ref("selenium")
const keywordInput     = ref("")
const keywords         = ref([])
const matchMode        = ref("any")
const status           = ref("Ready")
const statusClass      = ref("idle")
const loading          = ref(false)
const posts            = ref([])
const statusFilter     = ref("all")
const sortOrder        = ref("newest")

const successCount = computed(() => posts.value.filter(p => p.status === "generated").length)
const errorCount   = computed(() => posts.value.filter(p => p.status === "error").length)
const selectedCount = computed(() => posts.value.filter(p => p.selected).length)
const allSelected   = computed(() => posts.value.length > 0 && posts.value.every(p => p.selected))
const someSelected  = computed(() => posts.value.some(p => p.selected))
const filteredPosts = computed(() => {

  let result = [...posts.value]

  if (statusFilter.value !== "all") {
    result = result.filter(
      post => post.status === statusFilter.value
    )
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
  const post = posts.value[i]

  try {
    await api.delete("/comments/post", {
      params: { post_text: post.post_text }
    })
  } catch (err) {
    console.error("Failed to delete from CSV:", err)
  }

  posts.value.splice(i, 1)
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

async function runPipeline() {
  if (keywordInput.value.trim()) addKeyword()

  loading.value   = true
  status.value    = `Running ${selectedScraper.value} scraper...`
  statusClass.value = "running"
  posts.value     = []

  try {
    const params = {
      scraper_type: selectedScraper.value,
      match_mode: matchMode.value,
    }
    keywords.value.forEach(kw => {
      params["keywords"] = params["keywords"]
        ? [...[params["keywords"]].flat(), kw]
        : kw
    })

    await api.post(
      "/comments/run",
      null,
      { params }
    )

    const history = await getHistory()
    
    posts.value = history.map(post => ({
      ...post,
      editing: false,
     edited: post.status === "edited",
      edited_comment: post.generated_comment,
      selected: false
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
    selected: false
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
  background: #0a0a0a;
  display: flex;
  justify-content: center;
  padding: 40px 16px;
  font-family: 'Inter', system-ui, sans-serif;
  color: #e0e0e0;
}

.card {
  width: 100%;
  max-width: 1100px;
  background: #111;
  border: 1px solid #222;
  border-radius: 12px;
  overflow: hidden;
}

.header {
  padding: 32px 36px 24px;
  border-bottom: 1px solid #1e1e1e;
}
.header h1 { font-size: 1.6rem; font-weight: 600; color: #fff; }
.header p  { margin-top: 6px; color: #555; font-size: 0.875rem; }

.controls {
  padding: 28px 36px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-bottom: 1px solid #1e1e1e;
}

.field { display: flex; flex-direction: column; gap: 8px; }
.field label { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: .06em; }
.field label .hint { text-transform: none; letter-spacing: 0; color: #444; margin-left: 6px; }

select, input[type="text"], input:not([type]) {
  background: #0d0d0d;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 10px 14px;
  color: #e0e0e0;
  font-size: 0.9rem;
  outline: none;
  transition: border-color .2s;
  width: 100%;
  max-width: 460px;
}
select:focus, input:focus { border-color: #444; }

.tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.tag {
  display: flex; align-items: center; gap: 6px;
  background: #1a1a1a; border: 1px solid #2e2e2e;
  border-radius: 6px; padding: 4px 10px;
  font-size: 0.8rem; color: #ccc;
}
.tag button {
  background: none; border: none; color: #555;
  cursor: pointer; font-size: 1rem; line-height: 1;
  padding: 0;
}
.tag button:hover { color: #e05c5c; }

.toggle { display: flex; gap: 0; max-width: 260px; }
.toggle button {
  flex: 1; padding: 9px; background: #0d0d0d;
  border: 1px solid #2a2a2a; color: #555;
  font-size: 0.85rem; cursor: pointer; transition: all .15s;
}
.toggle button:first-child { border-radius: 8px 0 0 8px; }
.toggle button:last-child  { border-radius: 0 8px 8px 0; border-left: none; }
.toggle button.active { background: #1c1c1c; color: #e0e0e0; border-color: #444; }

.run-btn {
  align-self: flex-start;
  background: #fff; color: #000;
  border: none; border-radius: 8px;
  padding: 11px 28px; font-size: 0.9rem;
  font-weight: 600; cursor: pointer; transition: opacity .15s;
}
.run-btn:hover    { opacity: .85; }
.run-btn:disabled { opacity: .35; cursor: not-allowed; }

.status-bar {
  padding: 12px 36px;
  font-size: 0.82rem;
  display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid #1a1a1a;
  color: #555;
}
.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #333; flex-shrink: 0;
}
.status-bar.running .dot { background: #f0c040; }
.status-bar.running      { color: #f0c040; }
.status-bar.done    .dot { background: #4caf7d; }
.status-bar.done         { color: #4caf7d; }
.status-bar.error   .dot { background: #e05c5c; }
.status-bar.error        { color: #e05c5c; }

.stats {
  display: flex; gap: 0;
  border-bottom: 1px solid #1a1a1a;
}
.stat {
  flex: 1; padding: 20px 36px;
  display: flex; flex-direction: column; gap: 4px;
  border-right: 1px solid #1a1a1a;
}
.stat:last-child { border-right: none; }
.stat-num   { font-size: 1.6rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: .05em; }

/* ---------- Toolbar (select all / bulk delete) ---------- */

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 36px;
  border-bottom: 1px solid #1a1a1a;
}

.filter-select {
  background: #0d0d0d;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  color: #ddd;
  padding: 6px 12px;
  max-width: 180px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: #999;
  cursor: pointer;
  user-select: none;
}
.select-all input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #4caf7d;
  cursor: pointer;
}

.bulk-delete-btn {
  background: #200d0d;
  border: 1px solid #3a1818;
  color: #e07f7f;
  border-radius: 6px;
  padding: 7px 16px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.bulk-delete-btn:hover {
  background: #2a1010;
  border-color: #e05c5c;
  color: #ff8c8c;
}

/* ---------- Post cards ---------- */

.cards-wrap {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 20px 36px 36px;
}

.post-card {
  position: relative;
  display: flex;
  gap: 16px;
  background: #0d0d0d;
  border: 1px solid #1e1e1e;
  border-radius: 10px;
  padding: 18px 18px 18px 16px;
  transition: border-color .15s, background .15s;
}
.post-card.selected {
  border-color: #2e4a3a;
  background: #0e1410;
}
.post-card.error {
  border-left: 3px solid #e05c5c;
}
.post-card.generated {
  border-left: 3px solid #4caf7d;
}

.post-card-select {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding-top: 2px;
  flex-shrink: 0;
}
.post-card-select input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #4caf7d;
  cursor: pointer;
}
.post-index {
  font-size: 0.7rem;
  color: #444;
  font-weight: 600;
  letter-spacing: .03em;
}

.post-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}
@media (max-width: 760px) {
  .post-card-body {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

.col-label {
  display: block;
  font-size: 0.7rem;
  color: #555;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-weight: 600;
  margin-bottom: 8px;
}

.post-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.post-content {
  font-size: 0.85rem;
  line-height: 1.6;
  color: #ccc;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 240px;
  overflow-y: auto;
  padding-right: 6px;
}
.post-content::-webkit-scrollbar { width: 6px; }
.post-content::-webkit-scrollbar-thumb {
  background: #2a2a2a;
  border-radius: 3px;
}

.comment-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  border-top: 1px solid #1a1a1a;
  padding-top: 16px;
}
@media (max-width: 760px) {
  .comment-col {
    border-left: none;
    padding-left: 0;
    border-top: 1px solid #1a1a1a;
    padding-top: 16px;
  }
}

.comment-col-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.comment-col-head .col-label { margin-bottom: 0; }

/* Ensure comment text is visible regardless of CommentEditor's own styles */
.comment-col :deep(*) {
  color: #ddd;
}
.comment-col :deep(textarea),
.comment-col :deep(input) {
  background: #161616;
  border: 1px solid #2a2a2a;
  color: #ddd;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 500;
  white-space: nowrap;
}

.badge.generated {
  background: #0d2018;
  color: #4caf7d;
}

.badge.edited {
  background: #2a2200;
  color: #f0c040;
}

.badge.posted {
  background: #0d1a2a;
  color: #4da3ff;
}

.badge.error,
.badge.failed {
  background: #200d0d;
  color: #e05c5c;
}

.view-post-btn {
  display: inline-block;
  align-self: flex-start;
  padding: 5px 12px;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  background: #0d0d0d;
  color: #4caf7d;
  text-decoration: none;
  font-size: 0.78rem;
  transition: all .15s;
}
.view-post-btn:hover {
  background: #16241c;
  border-color: #4caf7d;
}

.delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  color: #333;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 4px 8px;
  border-radius: 4px;
  transition: color .15s, background .15s;
}
.delete-btn:hover {
  color: #e05c5c;
  background: #200d0d;
}

.empty { padding: 60px 36px; text-align: center; color: #333; font-size: 0.9rem; }
</style>