import api from "./api"

export async function improveComment(
  comment,
  instruction
) {

  const response = await api.post(
    "/comments/improve",
    {
      comment,
      instruction
    }
  )

  return response.data.comment
}