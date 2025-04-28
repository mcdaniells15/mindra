from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.normalizers import Lowercase, NFD, StripAccents, Sequence
from tokenizers.processors import TemplateProcessing
from config import TEXT_FILES, VOCAB_SIZE, TOKENIZER_PATH

tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.normalizer = Sequence([NFD(), Lowercase(), StripAccents()])
tokenizer.pre_tokenizer = Whitespace()

trainer = BpeTrainer(
    vocab_size=VOCAB_SIZE,
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
)

tokenizer.train(TEXT_FILES, trainer)

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[("[CLS]", 1), ("[SEP]", 2)],
)

tokenizer.save(TOKENIZER_PATH)
print(f"Tokenizer saved to {TOKENIZER_PATH}")
