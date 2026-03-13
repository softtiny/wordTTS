from .constants import UNITS, TEENS, TENS, THOUSANDS

def number_to_words(n: int) -> str:
    if n == 0: return "zero"
    if n < 0: return "minus " + number_to_words(abs(n))
    
    def _chunk(num):
        words = ""
        h, r = divmod(num, 100)
        if h > 0: words += UNITS[h] + " hundred" + (" " if r > 0 else "")
        if r >= 20:
            t, u = divmod(r, 10)
            words += TENS[t] + (" " + UNITS[u] if u > 0 else "")
        elif r > 9: words += TEENS[r - 10]
        elif r > 0: words += UNITS[r]
        return words.strip()

    parts, idx = [], 0
    while n > 0:
        if n % 1000 != 0:
            parts.append(_chunk(n % 1000) + (" " + THOUSANDS[idx] if idx > 0 else ""))
        n //= 1000
        idx += 1
    return " ".join(reversed(parts)).strip()