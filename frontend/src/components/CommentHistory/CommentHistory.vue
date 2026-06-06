<template>

  <div>

    <button
      class="btn btn-secondary mb-3"
      @click="loadHistory"
    >
      View Saved Comments
    </button>

    <table
      v-if="history.length"
      class="table table-striped"
    >

      <thead>
        <tr>
          <th>ID</th>
          <th>Post</th>
          <th>Comment</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>

        <tr
          v-for="item in history"
          :key="item.id"
        >
          <td>{{ item.id }}</td>

          <td>{{ item.post_text }}</td>

          <td>
           <CommentEditor :post="item" />
          </td>

          <td>{{ item.status }}</td>
        </tr>

      </tbody>

    </table>

  </div>

</template>

<script setup>

import { ref } from "vue"

import {
  getHistory
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
    edited_comment: item.generated_comment
  })
)
}

</script>