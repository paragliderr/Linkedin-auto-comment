import api from "./api"

export async function getHistory() {
  const response = await api.get("/history/")
  return response.data
}

export async function deletePost(postText) {
  await api.delete("/comments/post", {
    params: {
      post_text: postText
    }
  })
}