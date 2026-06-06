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

    </div>

    <div v-else>

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
import { updateComment } from "../../services/commentEditService"
const props = defineProps({
  post: Object
})

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

</script>