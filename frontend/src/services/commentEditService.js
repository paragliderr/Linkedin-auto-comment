import api from "./api"

export async function updateComment(id, editedComment) {

  const response = await api.post(
    "/comments/edit",
    {
      id,
      edited_comment: editedComment
    }
  )

  return response.data
}