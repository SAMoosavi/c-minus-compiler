def read_tokens(file_path):
    tokens = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # expect: lineno<TAB>(TYPE, value)
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            token = parts[1].strip()
            tokens.append(token)
    return tokens

def compare_tokens(tokens1, tokens2):
    total = min(len(tokens1), len(tokens2))
    match = 0
    for a, b in zip(tokens1, tokens2):
        if a == b:
            match += 1
    percent = (match / total) * 100 if total > 0 else 0
    return match, total, percent

def main():
    scanner_tokens = read_tokens('tokens.txt')
    antlr_tokens = read_tokens('ANTLR_p1.txt')

    match, total, percent = compare_tokens(scanner_tokens, antlr_tokens)

    print(f"✅ Matched {match}/{total} tokens")
    print(f"🎯 Match Accuracy: {percent:.2f}%")

    if len(scanner_tokens) != len(antlr_tokens):
        print(f"⚠️ Token count differs: custom = {len(scanner_tokens)}, ANTLR = {len(antlr_tokens)}")

if __name__ == "__main__":
    main()
