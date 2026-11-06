import re
import regex

def train_bpe (input_path:str, vocab_size:int = 266, special_tokens:list[str] = []): 
    """
    train bpe
    """
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()
    special_tokens_joined = "|".join(re.escape(token) for token in special_tokens)
    text = re.split(special_tokens_joined,text)
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    text_pretokenization = [[] for i in range(len(text))]
    word_frequencies = {}
    
    for i in range(len(text)):
        for j in regex.finditer(PAT, text[i]):
            text_pretokenization[i].append(j.group())

    for i in range(len(text_pretokenization)):
        for j in text_pretokenization[i]:
            word_frequencies[j] = word_frequencies.get(j, 0) + 1

    word_frequencies_encode = {}
    for word, frequency in word_frequencies.items():
        encoded = word.encode("utf-8")
        tokens = tuple(encoded[i:i+1] for i in range(len(encoded)))
        word_frequencies_encode[tokens] = word_frequencies_encode.get(tokens, 0) + frequency
    
    merge_result = []
    vocab = {i: bytes([i]) for i in range(256)}
    for i in range(len(special_tokens)):
        vocab[i + 256] = special_tokens[i].encode("utf-8")

    # while len(vocab) <  vocab_size:
    #     merge = {}
    #     for word, frequency in word_frequencies_encode.items():
    #         if len(word) > 1:
    #             for j in range(len(word) - 1):
    #                 tokens = (word[j], word[j+1])
    #                 merge[tokens] = merge.get(tokens, 0) + frequency
    #     if not merge:
    #         break
    #     best_pair = max(merge, key=lambda pair: (merge[pair], pair))
    #     merge_result.append(best_pair)
    #     vocab[len(vocab)] = best_pair[0] + best_pair[1]

    #     word_frequencies_encode_new = {}
    #     for word, frequency in word_frequencies_encode.items():
    #         word_new = []
    #         j = 0
    #         while j < len(word):
    #             if j + 1 < len(word) and (word[j], word[j+1]) == best_pair:
    #                 word_new.append(word[j] + word[j+1])
    #                 j += 2
    #             else:
    #                 word_new.append(word[j])
    #                 j += 1
    #         word_frequencies_encode_new[tuple(word_new)] = word_frequencies_encode_new.get(tuple(word_new), 0) + frequency
    #     word_frequencies_encode = word_frequencies_encode_new
    
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
<<<<<<< HEAD
        merge.pop(best_pair)
=======
>>>>>>> e622f274376e00b6fae96241d3a666f496b04d07

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
<<<<<<< HEAD
                            merge[(best_pair[1], best_pair[0])] = merge.get((best_pair[1], best_pair[0]), 0) - frequency

=======
                            merge[best_pair] = merge.get(best_pair, 0) - 2 * frequency
>>>>>>> e622f274376e00b6fae96241d3a666f496b04d07
        
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


