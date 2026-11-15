#!/usr/bin/env python3
"""批量最近邻匹配报表验收探针。

契约：
  from fuzzywuzzy.batch import nearest
  res = nearest(["a例"], candidates, threshold=80)
  res.matches  [{query, choice, score}]
  res.misses   未达阈值的 query 列表
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FAILED = 0
PASSED = 0


def check(code, desc, fn):
    global FAILED, PASSED
    try:
        fn()
        print(f"[PASS] {code} {desc}")
        PASSED += 1
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {code} {desc}")
        print(f"        {type(exc).__name__}: {exc}")
        FAILED += 1


def main():
    try:
        from fuzzywuzzy.batch import nearest  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] P0 导入 fuzzywuzzy.batch 失败：{type(exc).__name__}: {exc}")
        print("-" * 60)
        print("探针汇总：0/5 通过")
        return 1

    CAND = ["New York", "Los Angeles", "San Francisco"]

    def p1():
        res = nearest(["New York"], CAND)
        assert len(res.matches) == 1, res.matches
        assert res.matches[0].choice == "New York"

    def p2():
        res = nearest(["New Yrok"], CAND)
        assert res.matches[0].choice == "New York", res.matches[0].choice
        assert res.matches[0].score >= 80, res.matches[0].score

    def p3():
        res = nearest(["zzz"], CAND, threshold=90)
        assert res.matches == [], res.matches
        assert res.misses == ["zzz"], res.misses

    def p4():
        res = nearest(["New York", "Los Angeles"], CAND, threshold=90)
        assert len(res.matches) == 2, res.matches

    def p5():
        from fuzzywuzzy import fuzz
        assert fuzz.ratio("abc", "abc") == 100

    check("P1", "完全命中", p1)
    check("P2", "近似命中并给出分数", p2)
    check("P3", "低于阈值进 miss", p3)
    check("P4", "多条查询各自匹配", p4)
    check("P5", "既有 fuzz 不变", p5)

    print("-" * 60)
    print(f"探针汇总：{PASSED}/{PASSED + FAILED} 通过")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
