import re
import regex
from cs336_basics.pretokenization_example import find_chunk_boundaries
from multiprocessing import Pool

def process_chunk(text, PAT):
    word_frequencies = {}

    for piece in text:
        for j in regex.finditer(PAT, piece):
            word = j.group()
            word_frequencies[word] = (word_frequencies.get(word, 0) + 1)
    return word_frequencies

def train_bpe (input_path:str, vocab_size:int = 266, special_tokens:list[str] = []): 
    """
    train bpe
    """
    special_tokens_joined = "|".join(re.escape(token) for token in special_tokens)
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    word_frequencies = {}
    chunks = []
    num_processes = 4
    
    with open(input_path, "rb") as f:
        boundaries = find_chunk_boundaries(f, num_processes, b"<|endoftext|>")

        for start, end in zip(boundaries[:-1], boundaries[1:]):
            f.seek(start)
            chunk = f.read(end - start).decode("utf-8", errors="ignore")
            chunk= re.split(special_tokens_joined,chunk)
            chunks.append(chunk)
            # Run pre-tokenization on your chunk and store the counts for each pre-token

    tasks = [(chunk, PAT) for chunk in chunks]

    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_chunk, tasks)
    for i in range(len(chunks) - 1):
        for word, frequency in results[i + 1].items():
            results[0][word] = results[0].get(word, 0) + frequency
    word_frequencies = results[0]
    
    word_frequencies_encode = {}
    for word, frequency in word_frequencies.items():
        encoded = word.encode("utf-8")
        tokens = tuple(encoded[i:i+1] for i in range(len(encoded)))
        word_frequencies_encode[tokens] = word_frequencies_encode.get(tokens, 0) + frequency
    
    merge_result = []
    vocab = {i: bytes([i]) for i in range(256)}
    for i in range(len(special_tokens)):
        vocab[i + 256] = special_tokens[i].encode("utf-8")

    merge = {}
    for word, frequency in word_frequencies_encode.items():
        if len(word) > 1:
            for j in range(len(word) - 1):
                tokens = (word[j], word[j+1])
                merge[tokens] = merge.get(tokens, 0) + frequency
    best_pair = max(merge, key=lambda pair: (merge[pair], pair))
    merge_result.append(best_pair)
    vocab[len(vocab)] = best_pair[0] + best_pair[1]

    word_frequencies_encode_new = {}
    for word, frequency in word_frequencies_encode.items():
        word_new = []
        j = 0
        while j < len(word):
            if j + 1 < len(word) and (word[j], word[j+1]) == best_pair:
                word_new.append(word[j] + word[j+1])
                j += 2
            else:
                word_new.append(word[j])
                j += 1
        word_frequencies_encode_new[tuple(word_new)] = word_frequencies_encode_new.get(tuple(word_new), 0) + frequency
    word_frequencies_encode = word_frequencies_encode_new

    while len(vocab) <  vocab_size:
        merge.pop(best_pair)

        for word, frequency in word_frequencies_encode.items():
            if len(word) > 1:
                if best_pair[0] + best_pair[1] in word:
                    for j in range(len(word) - 1):
                        tokens = (word[j], word[j+1])
                        if tokens[0] == best_pair[0] + best_pair[1] and tokens[1] != best_pair[0] + best_pair[1]:
                            merge[tokens] = merge.get(tokens, 0) + frequency
                            merge[(best_pair[1], word[j+1])] = merge.get((best_pair[1], word[j+1]), 0) - frequency
                            merge[best_pair] = merge.get(best_pair, 0) -  frequency
                        elif tokens[1] == best_pair[0] + best_pair[1] and tokens[0] != best_pair[0] + best_pair[1]:
                            merge[tokens] = merge.get(tokens, 0) + frequency
                            merge[(word[j], best_pair[0])] = merge.get((word[j],best_pair[0]), 0) - frequency
                            merge[best_pair] = merge.get(best_pair, 0) -  frequency
                        elif tokens[0] == best_pair[0] + best_pair[1] and tokens[1] == best_pair[0] + best_pair[1]:
                            merge[tokens] = merge.get(tokens, 0) + frequency
                            merge[(best_pair[1], best_pair[0])] = merge.get((best_pair[1], best_pair[0]), 0) - frequency

        best_pair = max(merge, key=lambda pair: (merge[pair], pair))
        merge_result.append(best_pair)
        vocab[len(vocab)] = best_pair[0] + best_pair[1]
    
        word_frequencies_encode_new = {}
        for word, frequency in word_frequencies_encode.items():
            word_new = []
            j = 0
            while j < len(word):
                if j + 1 < len(word) and (word[j], word[j+1]) == best_pair:
                    word_new.append(word[j] + word[j+1])
                    j += 2
                else:
                    word_new.append(word[j])
                    j += 1
            word_frequencies_encode_new[tuple(word_new)] = word_frequencies_encode_new.get(tuple(word_new), 0) + frequency
        word_frequencies_encode = word_frequencies_encode_new

    return vocab, merge_result


