from tokenizers import Tokenizer
from config import TOKENIZER_PATH

tokenizer = Tokenizer.from_file(TOKENIZER_PATH)


def tokenize(text):
    output = tokenizer.encode(text)
    return output.tokens, output.ids


# Example
text = "Mindra transforms learning."
tokens, ids = tokenize(text)
print("Tokens:", tokens)
print("IDs:", ids)
