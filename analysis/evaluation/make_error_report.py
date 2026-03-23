from pathlib import Path
import re

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

ids = Path("Public_Data_TrainDev/Dev/dev_ids.txt").read_text(encoding="utf-8").splitlines()
gt  = Path("Public_Data_TrainDev/Dev/dev_gt_diac.txt").read_text(encoding="utf-8").splitlines()
pr  = Path("outputs/dev_pred_text_only.txt").read_text(encoding="utf-8").splitlines()

n = min(len(ids), len(gt), len(pr))

out = []
diff = 0
for i in range(n):
    g = norm_space(gt[i])
    p = norm_space(pr[i])

    if g != p:
        diff += 1
        out.append(f"ID: {ids[i]}")
        out.append(f"GT: {g}")
        out.append(f"PR: {p}")
        out.append("-" * 80)

Path("outputs/dev_errors_side_by_side.txt").write_text("\n".join(out), encoding="utf-8")
print(f"Total: {n}")
print(f"Mismatched sentences: {diff}")
print("Wrote outputs/dev_errors_side_by_side.txt")
