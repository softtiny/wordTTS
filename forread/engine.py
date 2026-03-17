from .constants import UNITS, TEENS, TENS, THOUSANDS
import re
import inflect

def convert_ordinal_to_word(ordinal_str):
    p = inflect.engine()
    
    # 1. 提取数字部分 (比如从 "1st" 提取出 1)
    match = re.search(r"\d+", str(ordinal_str))
    if not match:
        return "Invalid"
    
    num_int = int(match.group())
    
    # 2. 先把数字转成单词 (如: 1 -> "one", 100 -> "one hundred")
    word = p.number_to_words(num_int)
    
    # 3. 再把单词转成序数词单词 (如: "one" -> "first", "one hundred" -> "one hundredth")
    # 这种分步走的方法在所有 inflect 版本中都非常稳定
    ordinal_word = p.ordinal(word)
    
    #.capitalize()首字母大写
    # 4. 格式化输出：去除连字符
    return ordinal_word.replace('-', ' ')
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