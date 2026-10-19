#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把你自己的题目文本 / CSV 转成本项目能导入的 questions.json。

用法:
    python3 to_questions.py 我的题目.txt  questions.json
    python3 to_questions.py 我的题目.csv  questions.json

文本格式（题目之间空一行）:

    分类：马原 单选
    题干写在这里（ ）
    A. 选项一
    B. 选项二
    C. 选项三
    D. 选项四
    答案：A
    解析：可省略，写了更好

    题干（不写分类时，自动归到「我的题库」）
    A. 选项一
    B. 选项二
    C. 选项三
    D. 选项四
    答案：AC        ← 两个以上字母 = 多选

CSV 格式（用 Excel / WPS 就能编），表头固定为:
    题干,选项A,选项B,选项C,选项D,答案,分类,解析
    答案列: 单选写一个字母如 B; 多选连写如 ACD。分类、解析可留空。

只用你自己合法取得的题目（自己买的书、自己整理的笔记等），仅供个人学习。
"""
import sys, re, json, csv

LETTERS = 'ABCDEFGH'

def norm_answer(s):
    idx = [LETTERS.index(ch) for ch in s.strip().upper() if ch in LETTERS]
    return idx

def parse_txt(text):
    qs = []
    for block in re.split(r'\n\s*\n', text):
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        cat = None; stem_lines = []; options = []; answer = None; exp = []
        mode = 'stem'
        for ln in lines:
            if ln.startswith('分类：') or ln.startswith('分类:'):
                cat = ln.split('：', 1)[-1].split(':', 1)[-1].strip(); continue
            m = re.match(r'^([A-H])[\.、．:：]\s*(.+)$', ln)
            if m:
                options.append(m.group(2).strip()); mode = 'opt'; continue
            if ln.startswith('答案：') or ln.startswith('答案:'):
                answer = norm_answer(ln.split('：', 1)[-1].split(':', 1)[-1]); mode = 'ans'; continue
            if ln.startswith('解析：') or ln.startswith('解析:'):
                exp.append(ln.split('：', 1)[-1].split(':', 1)[-1].strip()); mode = 'exp'; continue
            if mode == 'exp': exp.append(ln)
            elif mode == 'stem': stem_lines.append(ln)
            elif mode == 'opt' and options: options[-1] += ln
        if not stem_lines or len(options) < 2 or not answer:
            print(f'跳过一段无法识别的内容: {" ".join(lines)[:40]}...', file=sys.stderr)
            continue
        multi = len(answer) > 1
        q = {
            'id': f'q{len(qs) + 1}',
            'cat': cat or f'我的题库 {"多选" if multi else "单选"}',
            'stem': ''.join(stem_lines),
            'options': options,
            'answer': answer if multi else answer[0],
        }
        if exp: q['explanation'] = ''.join(exp)
        qs.append(q)
    return qs

def parse_csv(path):
    qs = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            ans = norm_answer(row.get('答案', ''))
            opts = [row.get(f'选项{c}', '').strip() for c in 'ABCD']
            opts = [o for o in opts if o]
            if not row.get('题干') or len(opts) < 2 or not ans:
                continue
            multi = len(ans) > 1
            q = {
                'id': f'q{len(qs) + 1}',
                'cat': (row.get('分类') or '').strip() or f'我的题库 {"多选" if multi else "单选"}',
                'stem': row['题干'].strip(),
                'options': opts,
                'answer': ans if multi else ans[0],
            }
            if (row.get('解析') or '').strip(): q['explanation'] = row['解析'].strip()
            qs.append(q)
    return qs

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    if src.lower().endswith('.csv'):
        qs = parse_csv(src)
    else:
        qs = parse_txt(open(src, encoding='utf-8').read())
    if not qs:
        print('没有解析出任何题目，请检查格式。', file=sys.stderr); sys.exit(2)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(qs, f, ensure_ascii=False, indent=1)
    print(f'完成: {len(qs)} 道题 -> {dst}')

if __name__ == '__main__':
    main()
