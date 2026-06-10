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
      </div>

      <div class="table-wrap" v-if="posts.length">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Post</th>
              <th>Generated Comment</th>
              <th>Status</th>
              <th>Original Post</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(post, i) in posts"
              :key="i"
              :class="post.status"
            >
              <td class="num">{{ i + 1 }}</td>
              <td class="text">{{ post.post_text }}</td>
              <td> 
               <CommentEditor :post="post" />
              </td>
              <td>
                <span class="badge" :class="post.status">
                  {{ post.status }}
                </span>
              </td>
              <td>
               <a
                 v-if="post.post_url"
                 :href="post.post_url"
                 target="_blank"
                  class="view-post-btn"
                >
                  View Post
                </a>
              </td>
              <td>
              <button class="delete-btn" @click="removePost(i)" title="Remove row">✕</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <hr class="my-4">
      <CommentHistory />

      <div class="empty" v-if="!posts.length && !loading">
        Run the pipeline to see results here.
      </div>

    </div>
  </div>
</template>

<script setup>

import { ref, computed } from "vue"
import api from "./services/api"

import CommentEditor from "./components/CommentEditor/CommentEditor.vue"
import CommentHistory from "./components/CommentHistory/CommentHistory.vue"


const selectedScraper = ref("selenium")
const keywordInput     = ref("")
const keywords         = ref([])
const matchMode        = ref("any")
const status           = ref("Ready")
const statusClass      = ref("idle")
const loading          = ref(false)
const posts            = ref([])

const successCount = computed(() => posts.value.filter(p => p.status === "generated").length)
const errorCount   = computed(() => posts.value.filter(p => p.status === "error").length)

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


  const response = await api.post(
  "/comments/run",
  null,
  { params }
)

console.log(response.data)

posts.value = response.data.map(post => ({
  ...post,
  editing: false,
  edited: false,
  edited_comment: post.generated_comment
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
.delete-btn {
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

select, input {
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

.table-wrap { overflow-x: auto; padding: 0 36px 36px; }
table { width: 100%; border-collapse: collapse; margin-top: 24px; font-size: 0.85rem; }
th {
  text-align: left; padding: 10px 14px;
  color: #444; font-size: 0.75rem;
  text-transform: uppercase; letter-spacing: .06em;
  border-bottom: 1px solid #1e1e1e;
}
td { padding: 12px 14px; border-bottom: 1px solid #161616; vertical-align: top; }
tr:last-child td { border-bottom: none; }
td.num   { color: #444; width: 40px; }
td.text  { max-width: 360px; white-space: pre-wrap; word-break: break-word; color: #bbb; }

.badge {
  padding: 3px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 500;
}
.badge.generated { background: #0d2018; color: #4caf7d; }
.badge.error     { background: #200d0d; color: #e05c5c; }

.empty { padding: 60px 36px; text-align: center; color: #333; font-size: 0.9rem; }

.view-post-btn {
  display: inline-block;
  padding: 5px 12px;
  border: 1px solid #2a2a2a;
  border-radius: 6px;
  background: #0d0d0d;
  color: #4caf7d;
  text-decoration: none;
  font-size: 0.8rem;
  transition: all .15s;
}

.view-post-btn:hover {
  background: #16241c;
  border-color: #4caf7d;
}
</style>