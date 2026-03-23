from pathlib import Path
import re
from collections import Counter

DIACS = set("ًٌٍَُِّْ")
arabic_letter = re.compile(r"[\u0621-\u064A]")

def extract_diacritics(s: str):
    return [c for c in s if c in DIACS]

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def last_arabic_letter_pos(s: str) -> int:
    for i in range(len(s)-1, -1, -1):
        if arabic_letter.match(s[i]):
            return i
    return -1

ids = Path("Public_Data_TrainDev/Dev/dev_ids.txt").read_text(encoding="utf-8").splitlines()
gt  = Path("Public_Data_TrainDev/Dev/dev_gt_diac.txt").read_text(encoding="utf-8").splitlines()
pr  = Path("outputs/dev_pred_text_only.txt").read_text(encoding="utf-8").splitlines()

n = min(len(ids), len(gt), len(pr))

sent_diff = 0
case_end_like = 0
cat_counter = Counter()

for i in range(n):
    g = norm_space(gt[i])
    p = norm_space(pr[i])

    if g != p:
        sent_diff += 1

    # diacritics sequences (rough character-level view)
    gd = extract_diacritics(g)
    pd = extract_diacritics(p)

    # count which diacritics are "more/less" frequent in prediction than GT
    for d in DIACS:
        delta = p.count(d) - g.count(d)
        if delta != 0:
            cat_counter[f"count_diff_{d}"] += abs(delta)

    # proxy for case-ending (i'rab): compare last-letter + following diacritics
    gi = last_arabic_letter_pos(g)
    pi = last_arabic_letter_pos(p)
    if gi != -1 and pi != -1:
        g_tail = g[gi:gi+3]
        p_tail = p[pi:pi+3]
        if g_tail != p_tail:
            case_end_like += 1

print("Samples:", n)
print("Sentences mismatched:", sent_diff, f"({sent_diff/n:.1%})")
print("Case-ending proxy mismatches (sentences):", case_end_like, f"({case_end_like/n:.1%})")
print("\nLargest diacritic count-differences (rough):")
for k, v in cat_counter.most_common(10):
    print(" ", k, "=", v)
