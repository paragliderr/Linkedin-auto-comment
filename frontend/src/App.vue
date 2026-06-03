<template>
  <div class="container mt-5" style="max-width: 1200px;">

    <div class="card shadow p-4">

      <h1 class="text-primary mb-4">
        LinkedIn Auto Comment Generator
      </h1>
      <p class="text-muted mb-4">
       Generate AI-powered comments from LinkedIn posts using Playwright or Selenium.
      </p>

      <div class="mb-3">
        <label class="form-label">
          Select Scraper
        </label>

        <select
          class="form-select"
          v-model="selectedScraper"
        >
          <option value="playwright">
            Playwright
          </option>

          <option value="selenium">
            Selenium
          </option>
        </select>
      </div>

      <button
        class="btn btn-primary mb-3"
        @click="runPipeline"
      >
        Generate Comments
      </button>

      <div class="alert alert-info">
        <strong>🟢 Status:</strong> {{ status }}
     </div>

      <h3 class="mt-4">
        Generated Comments
      </h3>

      <table class="table table-hover table-striped align-middle mt-3">

        <thead>
          <tr>
            <th>Post</th>
            <th>Comment</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="(post,index) in posts"
            :key="index"
          >
            <td>{{ post.post_text }}</td>
            <td>{{ post.generated_comment }}</td>
          </tr>
        </tbody>

      </table>

    </div>

  </div>
</template>

<script setup>
import { ref } from "vue"
import api from "./services/api";

const selectedScraper = ref("playwright")

const status = ref("Ready")

const posts = ref([])

async function runPipeline() {
  try {
    status.value = `Running ${selectedScraper.value} scraper...`

    const response = await api.post(
      "/comments/run",
      null,
      {
        params: {
          scraper_type: selectedScraper.value
        }
      }
    )
    
    console.log(response.data)

    posts.value = response.data
    status.value = "Pipeline completed"
  }
  catch (error) {
    console.error(error)
    status.value = "Pipeline failed"
  }
}
</script>