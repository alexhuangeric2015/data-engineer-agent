from pathlib import Path
import re
ROOT=Path(__file__).parent;SOURCE=ROOT/'lib/content_layouts.py';src=SOURCE.read_text();start=src.index('# 01 cover')
pre=src[:start].replace('图解架构版_V5','架构视觉版_V7').replace('图解架构版V5','架构视觉版V7')
exec(compile(pre,str(__file__),'exec'))
exec(compile((ROOT/'lib/refined_system.py').read_text(),str(__file__),'exec'))
exec(compile((ROOT/'visual_system.py').read_text(),str(__file__),'exec'))
for b in re.split(r'(?m)(?=^# \d\d )',src[start:]):
    if not b.strip():continue
    num=int(re.match(r'# (\d\d)',b).group(1));p=ROOT/'pages'/f'{num:02d}.py'
    if p.exists():exec(compile(p.read_text(),str(p),'exec'))
    else:exec(compile(b.split('assert len(prs.slides)==30')[0],str(SOURCE),'exec'))
prs.core_properties.title='HiAgent企业数据智能体建设规划｜架构视觉版V7'
assert len(prs.slides)==30
prs.save(OUT)
(ROOT/'slides_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));(ROOT/'speaker_notes.json').write_text(json.dumps(notes_out,ensure_ascii=False,indent=2));(ROOT/'qa/textboxes.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
a=['# 架构视觉版V7｜逐页汇报提纲','']
for r in notes_out:a.extend([f"## {r['page']:02d} {r['title']}",'',r['notes'],''])
(ROOT/'逐页汇报提纲.md').write_text('\n'.join(a));print(OUT)
