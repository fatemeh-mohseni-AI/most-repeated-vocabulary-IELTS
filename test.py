import re

text = "you\nabout"
text = text.replace("\n", " ")
text = re.sub(r'[^\w\s]', '', text) # Removing Non-Alphanumeric Characters
words = text.lower().split(" ")
print(words)