<template>
  <div>

    <div v-if="!post.editing">

      {{ post.edited_comment }}

      <span
      v-if="post.edited"
     class="badge bg-warning text-dark ms-2"
      >
     Edited
     </span>

      <button
        class="btn btn-sm btn-outline-primary ms-2"
        @click="
         post.original_comment = post.edited_comment;
         post.editing = true
         "
      >
        Edit
      </button>

      <button
         class="btn btn-sm btn-outline-success ms-2"
         @click="openAssistant"
      >
       AI Assistant
      </button>
      <button
  class="btn btn-sm btn-outline-success ms-2"
  :disabled="posting || post.posted"
  @click="postToLinkedIn"
>
  {{ post.posted ? "Posted ✓" : (posting ? "Posting..." : "Post Comment") }}
</button>

<span v-if="postStatus === 'failed'" class="badge bg-danger ms-2">
  Failed to post
</span>
    </div>

    <div
       v-if="showAssistant"
      class="card mt-2 p-3"
    >
      <h6>AI Comment Assistant</h6>

   <div
     v-for="(msg,index) in messages"
      :key="index"
      class="mb-2"
    >
        <strong>{{ msg.role }}:</strong>
      {{ msg.content }}
  </div>

  <textarea
    class="form-control"
    rows="2"
    v-model="userPrompt"
    placeholder="Tell AI how to improve this comment..."
  ></textarea>

  <button
    class="btn btn-primary btn-sm mt-2 me-2"
    @click="sendPrompt"
  >
    Send
  </button>

  <button
  class="btn btn-success btn-sm mt-2 me-2"
  @click="applySuggestion"
 >
  Apply Suggestion
 </button>

  <button
    class="btn btn-secondary btn-sm mt-2"
    @click="showAssistant = false"
  >
    Close
  </button>
 </div>

    <div v-if="post.editing">

      <textarea
        class="form-control"
        rows="3"
        v-model="post.edited_comment"
      ></textarea>

      <button
        class="btn btn-success btn-sm mt-2 me-2"
        @click="saveEdit"
      >
        Save
      </button>

      <button
       class="btn btn-warning btn-sm mt-2 me-2"
       @click="undoEdit"
     >
       Undo
     </button>

      <button
        class="btn btn-secondary btn-sm mt-2"
        @click="cancelEdit"
      >
        Cancel
      </button>

    </div>

  </div>
</template>

<script setup>
import { ref } from "vue"
import { updateComment } from "../../services/commentEditService"
import { improveComment } from "../../services/aiAssistantService"
import api from "../../services/api"

const posting = ref(false)
const postStatus = ref("")

async function postToLinkedIn() {
  if (!props.post.post_url) {
    alert("No post URL available")
    return
  }

  if (!confirm("This will post the comment live on LinkedIn. Continue?")) {
    return
  }

  posting.value = true
  postStatus.value = ""

  try {
    const response = await api.post("/comments/post-to-linkedin", {
      post_url: props.post.post_url,
      comment_text: props.post.edited_comment
    })

    if (response.data.success) {
      postStatus.value = "posted"
      props.post.posted = true
    } else {
      postStatus.value = "failed"
    }
  } catch (err) {
    console.error(err)
    postStatus.value = "failed"
  } finally {
    posting.value = false
  }
}
const props = defineProps({
  post: Object
})
const showAssistant = ref(false)

const userPrompt = ref("")

const messages = ref([])

const latestSuggestion = ref("")

function openAssistant() {

  showAssistant.value = true

  messages.value = [
    {
      role: "assistant",
      content: props.post.edited_comment
    }
  ]
}

async function saveEdit() {

  try {
    console.log(props.post)
    await updateComment(
      props.post.id,
      props.post.edited_comment
    )

    props.post.generated_comment =
      props.post.edited_comment

    props.post.edited = true

    props.post.editing = false

  }
  catch (error) {

    console.error(error)

    alert("Failed to save comment")

  }

}

function cancelEdit() {
  props.post.edited_comment =
    props.post.generated_comment

  props.post.editing = false
}

function undoEdit() {

  props.post.edited_comment =
    props.post.original_comment

}

async function sendPrompt() {

  try {

    messages.value.push({
      role: "user",
      content: userPrompt.value
    })

    const improved = await improveComment(
      props.post.edited_comment,
      userPrompt.value
    )

    messages.value.push({
      role: "assistant",
      content: improved
    })

    latestSuggestion.value = improved

    userPrompt.value = ""

  } catch (err) {

    console.error(err)

    alert("AI assistant failed")

  }
}

async function applySuggestion() {

  if (!latestSuggestion.value) {
    return
  }

  try {

    await updateComment(
      props.post.id,
      latestSuggestion.value
    )

    props.post.edited_comment =
      latestSuggestion.value

    props.post.generated_comment =
      latestSuggestion.value

    props.post.edited = true

    alert("Suggestion applied and saved")

  } catch (err) {

    console.error(err)

    alert("Failed to save suggestion")

  }
}

</script>