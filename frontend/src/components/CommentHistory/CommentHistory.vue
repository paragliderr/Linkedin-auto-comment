<template>

  <div class="history-section">

  <div class="history-header">
    <h2>Comment History</h2>
    <p>View and manage previously generated comments</p>
  </div>

  <button
      class="history-btn"
      @click="loadHistory"
    >
      View Saved Comments
    </button>

    <table
      v-if="history.length"
      class="history-table"
    >

      <thead>
        <tr>
          <th>ID</th>
          <th>Post</th>
          <th>Comment</th>
          <th>Status</th>
          <th>Original Post</th>
          <th></th>
        </tr>
      </thead>

      <tbody>

        <tr
          v-for="(item,index) in history"
          :key="item.id"
        >
          <td>{{ item.id }}</td>

         <td class="post-cell">

           <span v-if="!item.showFull">
             {{
                  item.post_text.length > 150
                 ? item.post_text.slice(0,150)
                 : item.post_text
             }}
          </span>

          <span v-else>
             {{ item.post_text }}
          </span>

         <button
              v-if="item.post_text.length > 150"
             class="view-btn"
             @click="item.showFull = !item.showFull"
             >
             {{ item.showFull ? "Show Less" : "Show More" }}
         </button>
         </td>

          <td>
           <CommentEditor :post="item" />
          </td>

          <td>
          <span class="badge" :class="item.status">
          {{ item.status }}
           </span>
          </td>
          <td>
           <a
           v-if="item.post_url"
           :href="item.post_url"
           target="_blank"
           class="view-post-btn"
           >
            View Post
           </a>
         </td>

          <td>
          <button
          class="delete-btn"
          @click="removeHistoryItem(index)"
          title="Remove row"
          >
            ✕
           </button>
          </td>
        </tr>

      </tbody>

    </table>

  </div>

</template>

<script setup>

import { ref } from "vue"

import {
  getHistory,
  deletePost
} from "../../services/historyService"

import CommentEditor
from "../CommentEditor/CommentEditor.vue"

const history = ref([])

async function loadHistory() {

  history.value = (await getHistory()).map(
  item => ({
    ...item,
    editing: false,
    edited: item.status === "edited",
    edited_comment: item.generated_comment,
    showFull: false
  })
)
}

async function removeHistoryItem(index) {

  if (!confirm("Delete this comment?")) {
  return
  }

  const item = history.value[index]

  try {
    await deletePost(item.post_text)
    history.value.splice(index, 1)
  } catch (err) {
    console.error(err)
  }
}

</script>

<style scoped>

.history-section {
  margin-top: 40px;
}

.history-header {
  margin-bottom: 20px;
}

.history-header h2 {
  color: white;
  font-size: 1.3rem;
}

.history-header p {
  color: #666;
  margin-top: 4px;
}

.history-btn {
  background: white;
  color: black;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 20px;
}

.history-btn:hover {
  opacity: .85;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 10px 14px;
  color: #444;
  border-bottom: 1px solid #1e1e1e;
}

td {
  padding: 12px 14px;
  border-bottom: 1px solid #161616;
  vertical-align: top;
}

.post-cell {
  max-width: 350px;
  color: #bbb;
}

.badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
}

.badge.generated {
  background: #0d2018;
  color: #4caf7d;
}

.badge.edited {
  background: #2a2200;
  color: #f0c040;
}

.badge.error {
  background: #200d0d;
  color: #e05c5c;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  background: transparent;
}

.history-table th {
  color: #444;
  border-bottom: 1px solid #1e1e1e;
}

.history-table td {
  color: #bbb;
  border-bottom: 1px solid #161616;
  padding: 12px 14px;
}

.view-btn {
  display: block;
  margin-top: 8px;
  background: none;
  border: none;
  color: #4caf7d;
  cursor: pointer;
  font-size: 0.8rem;
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