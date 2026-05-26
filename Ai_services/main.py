from chatbot import generate_comment

print("\n=== LinkedIn AUTO COMMENT ===\n")

post = input("Paste LinkedIn Post:\n\n")
print("\nGenerating comment...\n")
comment = generate_comment(post)
print("AI Comment:\n")
print(comment) 