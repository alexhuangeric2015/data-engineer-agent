"""Generate matching SVG previews and native, editable draw.io planning views."""
from pathlib import Path
from html import escape
import json
import xml.etree.ElementTree as E

ROOT = Path(__file__).parent
OUT = ROOT / 'diagrams'
OUT.mkdir(exist_ok=True)
NAVY='#163456'; BLUE='#2861B5'; TEAL='#087E72'; PURPLE='#7653A8'
INK='#20354D'; MUTED='#60758C'; LINE='#D7E1ED'; BG='#F3F6FA'
PALE='#EBF2FC'; GREEN='#E6F5F0'; WHITE='#FFFFFF'
FONT='Noto Sans CJK SC'

class Page:
    def __init__(self, name, title, subtitle, h=1200):
        self.name=name; self.w=2400; self.h=h; self.svg=[]; self.i=0; self.positions={'1':(0,0)}; self.boxes={}
        self.model=E.Element('mxGraphModel',dx='2400',dy=str(h),grid='1',gridSize='10',page='1',pageScale='1',pageWidth='2400',pageHeight=str(h),background=BG)
        self.root=E.SubElement(self.model,'root'); E.SubElement(self.root,'mxCell',id='0'); E.SubElement(self.root,'mxCell',id='1',parent='0')
        self.rect(0,0,2400,h,BG,stroke=BG)
        self.rect(0,0,2400,116,NAVY,stroke=NAVY)
        self.txt(48,17,2280,24,'HIAGENT  /  DATA INTELLIGENCE',15,'#AFC7E6',bold=True)
        self.txt(48,45,2280,47,title,33,WHITE,bold=True)
        self.txt(48,129,2280,32,subtitle,18,MUTED)
        self.txt(48,h-40,1870,24,'规划讨论稿 V0.3  ·  2026.10.27  ·  绿色突出当前建设范围，其他为目标规划；不表示已投产或通过验收。',16,MUTED)
        self.txt(2110,h-40,240,24,'治理与协同版 V0.3',15,MUTED,align='right')
    def uid(self): self.i+=1; return 'n'+str(self.i)
    def rect(self,x,y,w,h,fill=WHITE,stroke=LINE,r=12,parent='1',dash=False):
        n=self.uid(); px,py=self.positions[parent]; self.positions[n]=(x,y)
        self.boxes[n]=(x,y,w,h)
        style=f'rounded={int(r>0)};arcSize=10;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};strokeWidth=1.3;container=1;collapsible=0;'
        if dash: style+='dashed=1;'
        c=E.SubElement(self.root,'mxCell',id=n,value='',style=style,vertex='1',parent=parent)
        E.SubElement(c,'mxGeometry',x=str(x-px),y=str(y-py),width=str(w),height=str(h),attrib={'as':'geometry'})
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
        return n
    def txt(self,x,y,w,h,text,size=20,color=INK,bold=False,align='left',parent='1'):
        n=self.uid(); px,py=self.positions[parent]; lines=text.split('\n')
        style=f'text;html=0;whiteSpace=wrap;overflow=hidden;align={align};verticalAlign=middle;fontFamily={FONT};fontSize={size};fontColor={color};fontStyle={int(bold)};spacing=0;strokeColor=none;fillColor=none;'
        c=E.SubElement(self.root,'mxCell',id=n,value=text,style=style,vertex='1',parent=parent)
        E.SubElement(c,'mxGeometry',x=str(x-px),y=str(y-py),width=str(w),height=str(h),attrib={'as':'geometry'})
        anchor={'left':'start','center':'middle','right':'end'}[align]; tx=x if align=='left' else x+w/2 if align=='center' else x+w
        lh=size*1.48; start=y+h/2-(len(lines)-1)*lh/2
        for k,s in enumerate(lines):
            self.svg.append(f'<text x="{tx}" y="{start+k*lh}" dominant-baseline="central" text-anchor="{anchor}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(s)}</text>')
        return n
    def line(self,pts,color=BLUE,dash=False,arrow=True,source=None,target=None):
        n=self.uid(); style=f'edgeStyle=none;rounded=0;html=0;strokeColor={color};strokeWidth=2;endArrow={"block" if arrow else "none"};endFill=1;'
        if dash: style+='dashed=1;'
        def anchor(pt):
            candidates=[]
            for key,(x,y,w,h) in self.boxes.items():
                a,b=pt
                if x-5<=a<=x+w+5 and y-5<=b<=y+h+5 and min(abs(a-x),abs(a-x-w),abs(b-y),abs(b-y-h))<=5:
                    candidates.append((w*h,key))
            return min(candidates)[1] if candidates else None
        source=source or anchor(pts[0]); target=target or anchor(pts[-1])
        for key,pt,prefix in [(source,pts[0],'exit'),(target,pts[-1],'entry')]:
            if key:
                x,y,w,h=self.boxes[key];a=max(0,min(1,(pt[0]-x)/w));b=max(0,min(1,(pt[1]-y)/h))
                style+=f'{prefix}X={a};{prefix}Y={b};{prefix}Perimeter=0;'
        at=dict(id=n,style=style,edge='1',parent='1')
        if source: at['source']=source
        if target: at['target']=target
        c=E.SubElement(self.root,'mxCell',**at); g=E.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'})
        E.SubElement(g,'mxPoint',x=str(pts[0][0]),y=str(pts[0][1]),attrib={'as':'sourcePoint'})
        E.SubElement(g,'mxPoint',x=str(pts[-1][0]),y=str(pts[-1][1]),attrib={'as':'targetPoint'})
        if len(pts)>2:
            a=E.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in pts[1:-1]: E.SubElement(a,'mxPoint',x=str(x),y=str(y))
        path='M '+' L '.join(f'{x},{y}' for x,y in pts)
        self.svg.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="7 5"' if dash else '')+(f' marker-end="url(#{color[1:]})"' if arrow else '')+'/>')
    def pill(self,x,y,w,label,color=BLUE,fill=PALE,parent='1'):
        n=self.rect(x,y,w,30,fill,fill,15,parent)
        self.txt(x+8,y+1,w-16,28,label,15,color,True,'center',n); return n
    def card(self,x,y,w,h,title,body='',color=BLUE,fill=WHITE,parent='1',title_size=21):
        n=self.rect(x,y,w,h,fill,LINE,12,parent)
        self.rect(x+15,y+20,4,25,color,color,2,n)
        self.txt(x+31,y+14,w-46,37,title,title_size,color,True,parent=n)
        if body:self.txt(x+24,y+58,w-48,h-70,body,17,MUTED,parent=n)
        return n
    def layer(self,y,h,num,title,subtitle):
        n=self.rect(48,y,1704,h,WHITE,LINE)
        lab=self.rect(48,y,205,h,NAVY,NAVY,parent=n)
        self.txt(65,y+12,170,30,num+'  '+title,21,WHITE,True,parent=lab)
        self.txt(70,y+51,162,h-63,subtitle,16,'#C4D4E8',parent=lab)
        return n
    def save(self):
        defs=''.join(f'<marker id="{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>' for c in [BLUE,TEAL,PURPLE,MUTED,NAVY])
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="{self.h}" viewBox="0 0 2400 {self.h}"><defs>{defs}</defs><g font-family="{FONT},sans-serif">'+''.join(self.svg)+'</g></svg>'
        (OUT/(self.name+'.svg')).write_text(svg)
        f=E.Element('mxfile',host='app.diagrams.net',version='24.7.17'); d=E.SubElement(f,'diagram',id=self.name[:2],name=self.name); d.append(self.model)
        E.indent(f); E.ElementTree(f).write(OUT/(self.name+'.drawio'),encoding='utf-8',xml_declaration=True)


p=Page('01-数据智能体能力全景-V0.3','数据智能体能力全景｜专业协同与资产治理','专业 Agent 自主规划、按需引用其他 Agent；治理已有数据与知识，血缘能力通过数据资产平台提供。',1740)

def band(y,h,no,title,explain):
    group=p.rect(48,y,1792,h,WHITE,LINE)
    lab=p.rect(48,y,225,h,NAVY,NAVY,parent=group)
    p.txt(68,y+14,195,31,no+'  '+title,22,WHITE,True,parent=lab)
    p.txt(70,y+55,182,h-67,explain,17,'#C4D4E8',parent=lab)
    return group

# 01 — business spaces, not a new agent coordinator tier.
g=band(190,124,'01','业务场景','工作空间\n面向谁、完成什么工作')
for i,(a,b) in enumerate([
    ('数据研发','需求 · 设计 · 开发 · 交付'),('资产服务','找数据 · 理解数据 · 用数据'),
    ('治理运营','标准 · 质量 · 资产完善'),('运行保障','监测 · 排障 · 运行优化'),
    ('分析决策','问数 · 分析 · 洞察建议')]):
    p.card(293+i*308,203,292,98,a,b,BLUE,parent=g,title_size=22)

# 02 — all nine specialists can own a task and call other Agents as needed.
g=band(330,380,'02','专业智能体','三类九种专业角色\n内部规划、按需协作')
prod=p.rect(293,345,780,228,BG,LINE,parent=g)
p.txt(313,355,740,35,'数据生产类智能体 · 5 种',23,BLUE,True,parent=prod)
for i,(a,b) in enumerate([
    ('数据需求分析','目标 / 范围 / 口径'),('数据设计','模型 / 方案 / 标准'),
    ('数据开发','代码 / 加工 / 作业'),('数据测试','用例 / 对账 / 验证'),
    ('数据评审','检查 / 评审 / 建议')]):
    x=309+i*150;n=p.rect(x,407,140,111,WHITE,LINE,parent=prod)
    p.txt(x+5,416,130,57,a+'\n智能体',18,BLUE,True,'center',n)
    p.txt(x+5,485,130,23,b,13,MUTED,False,'center',n)
p.txt(313,534,740,24,'围绕需求到交付，形成专业分工与质量把关',17,MUTED,parent=prod)
ops=p.rect(1089,345,455,228,BG,LINE,parent=g)
p.txt(1109,355,415,35,'数据运营类智能体 · 3 种',23,BLUE,True,parent=ops)
for i,(a,b) in enumerate([('数据资产','当前建设'),('数据运维','运行保障'),('数据治理','治理辅助')]):
    x=1104+i*143;n=p.rect(x,407,136,111,GREEN if i==0 else WHITE,TEAL if i==0 else LINE,parent=ops)
    p.txt(x+5,416,126,57,a+'\n智能体',18,TEAL if i==0 else BLUE,True,'center',n)
    p.txt(x+5,485,126,23,b,14,TEAL if i==0 else MUTED,i==0,'center',n)
p.txt(1109,534,415,24,'当前资产查询：表、字段、字典及码值',17,MUTED,parent=ops)
analysis=p.rect(1560,345,260,228,BG,LINE,parent=g)
p.txt(1576,355,228,35,'分析挖掘类 · 1 种',22,PURPLE,True,parent=analysis)
n=p.rect(1576,407,228,111,WHITE,LINE,parent=analysis)
p.txt(1586,418,208,49,'数据分析智能体',21,PURPLE,True,'center',n)
p.txt(1586,485,208,23,'分析 / 挖掘 / 洞察',16,MUTED,False,'center',n)
p.txt(1576,534,228,24,'辅助分析与业务判断',17,MUTED,parent=analysis)
run=p.rect(293,590,1527,101,PALE,LINE,parent=g)
p.txt(310,598,1493,30,'各专业 Agent 内部运行机制｜提示词与 SKILL 约束处理方法，Agent 组织资源与实际调用',20,BLUE,True,parent=run)
for i,title in enumerate(['理解需求','任务规划','按需引用其他 Agent','工具调用','核验与汇总','人工确认']):
    x=310+i*250;n=p.rect(x,641,232,33,WHITE,LINE,parent=run)
    p.txt(x+6,642,220,31,title,17,BLUE,True,'center',n)

# 03 — lineage tools access the authoritative enterprise platform.
g=band(726,156,'03','规则与工具','提示词、SKILL 与工具\n支撑专业任务执行')
for i,(a,b) in enumerate([
    ('提示词与 SKILL 规则','职责边界 / 任务规划 / 其他 Agent 引用条件\n查询方法 / 设计规范 / 测试评审规则 / 分析方法'),
    ('资源访问与平台调用','知识检索 / 元数据与字典查询\n血缘查询：调用数据资产平台'),
    ('专业计算与成果生成','SQL 检查 / 数据探查 / 计算分析\n代码处理 / 图表生成 / 文档编制')]):
    p.card(293+i*514,739,499,114,a,b,BLUE,parent=g,title_size=22)
p.txt(307,852,1496,23,'Agent 引用其他 Agent、SKILL、知识库、数据库及工具；SKILL 定义规则，不建立资源引用。',17,MUTED,parent=g)

# 04 — semantics are governed enterprise definitions; lineage is read live from its platform.
g=band(898,132,'04','业务语义','领域知识与业务规则\n统一业务与数据理解')
for i,(a,b) in enumerate([
    ('业务概念','术语 / 业务对象 / 业务含义'),('指标口径','粒度 / 维度 / 计算定义'),
    ('模型语义','分层 / 实体 / 关联约束'),('标准与规范','命名 / 质量 / 设计评审'),
    ('映射与责任','业务技术映射 / 归属责任')]):
    p.card(293+i*308,913,292,102,a,b,BLUE,parent=g,title_size=22)

# 05 — foundation work governs existing assets; it does not wait for a governance Agent.
g=band(1046,280,'05','治理与资产','数据与知识基础建设\n治理存量与知识\n形成可信资产')
p.txt(310,1057,1493,31,'已有数据与知识的治理加工｜资产资料治理先行，数据治理智能体逐步辅助治理工作',21,BLUE,True,parent=g)
for i,title in enumerate(['资产收集','清洗校验','标准映射','语义补全','责任确认','发布更新']):
    x=293+i*257;n=p.rect(x,1102,235,45,PALE,LINE,parent=g)
    p.txt(x+8,1107,219,35,title,20,BLUE,True,'center',n)
    if i<5:p.line([(x+239,1124),(x+252,1124)],BLUE)
p.card(293,1164,755,143,'治理后的结构化数据资产','表与字段 / 字典码值 / 有效映射\n形成查询数据，支撑资产事实核验',BLUE,parent=g,title_size=22)
p.card(1064,1164,756,143,'治理后的知识资产','业务说明 / 标准规范 / 代码与分析案例\n形成知识库内容，支撑语义检索与候选定位',PURPLE,parent=g,title_size=22)

# 06 — existing assets and platform lineage are explicitly separate inputs.
g=band(1342,145,'06','企业系统与来源','已有资产与权威来源\n接入系统、复用成果')
p.card(293,1356,499,116,'已有数据资产','表结构 / 字段说明 / 字典与码值\n接入后按规则治理、维护与更新',BLUE,parent=g,title_size=22)
platform=p.card(807,1356,499,116,'数据资产平台','提供血缘查询接口与实际血缘结果\n支撑上下游追溯、变更影响分析',PURPLE,'#F3EFFA',parent=g,title_size=22)
p.card(1321,1356,499,116,'其他企业系统与知识来源','开发 / 治理 / 调度 / 分析等系统\n业务系统 / 数据仓库 / 标准与项目文档',BLUE,parent=g,title_size=22)

# HiAgent hosting and governance are support columns, not additional business Agents.
p.card(1860,190,282,124,'规划要点','Agent 规划 / 按需协作\n存量治理 / 平台血缘调用',BLUE,PALE,title_size=23)
hi=p.rect(1860,330,282,996,'#EDF3FC',BLUE)
p.txt(1880,347,242,36,'HiAgent 平台支撑',23,BLUE,True,parent=hi)
p.txt(1880,389,242,49,'承载专业 Agent\n复用平台资源与交互能力',17,MUTED,parent=hi)
for i,(a,b) in enumerate([
    ('Agent 承载','角色提示词 / SKILL\n专业 Agent 配置'),
    ('Agent 间引用','按需引用其他 Agent\n返回结果并由调用方汇总'),
    ('知识与数据接入','知识库检索\n数据库查询 / 工具接入'),
    ('会话与交互','连续对话 / 上下文\n执行反馈与结果展示')]):
    p.card(1876,463+i*164,250,142,a,b,BLUE,WHITE,parent=hi,title_size=22)
p.txt(1882,1150,238,138,'提示词与 SKILL 定义方法\n由专业 Agent 规划与调用\n\n具体能力以平台配置\n和实际验证为准',17,MUTED,parent=hi)
p.card(1860,1342,282,145,'企业资源接入','对接相关企业平台\n资产与血缘保持来源可追溯',BLUE,PALE,title_size=23)
guard=p.rect(2162,190,190,1297,NAVY,NAVY)
p.txt(2177,212,160,40,'贯穿保障',25,WHITE,True,'center',guard)
for i,(a,b) in enumerate([
    ('权限与安全','身份与授权\n数据访问边界'),('质量与评估','资产资料质量\n任务与回答质量'),
    ('审计与追溯','调用与操作记录\n成果依据追溯'),('治理与维护','标准与责任落实\n内容校验与更新'),
    ('人工与责任','业务口径确认\n治理与成果确认')]):
    n=p.rect(2175,294+i*210,164,170,'#214568','#3A5C7E',parent=guard)
    p.txt(2185,309+i*210,144,35,a,21,WHITE,True,'center',n)
    p.txt(2185,356+i*210,144,82,b,17,'#D2DFED',False,'center',n)
p.txt(2177,1370,160,71,'覆盖各层\n贯穿建设与使用过程',17,'#D2DFED',False,'center',guard)

# A highlighted call relationship avoids implying locally inferred or regenerated lineage.
chain=p.rect(48,1506,2304,100,'#F0EBF8','#D5C6E9')
p.txt(70,1515,2260,28,'血缘能力调用关系｜按需调用数据资产平台，返回血缘事实，再由 Agent 解释与辅助分析',21,PURPLE,True,'center',chain)
for i,title in enumerate(['专业 Agent','血缘查询工具 / 平台接口','数据资产平台','血缘事实与来源','追溯 / 影响分析结果']):
    x=80+i*458;n=p.rect(x,1558,421,34,WHITE,'#D5C6E9',parent=chain)
    p.txt(x+7,1559,407,32,title,18,PURPLE,True,'center',n)
    if i<4:p.line([(x+427,1575),(x+451,1575)],PURPLE)
p.txt(49,1626,2302,27,'规划口径：任务规划与协作属于专业 Agent 的内部能力；已有资产需治理，基础治理工作不依赖先建成数据治理 Agent。',19,NAVY,True,'center')
p.txt(49,1660,2302,23,'当前聚焦资产查询及其资料治理；血缘接入和其他专业能力纳入后续规划，数据资产平台的实际覆盖范围决定血缘分析范围。',17,MUTED,align='center')
p.save()
print('Generated V0.3:',p.w,p.h)
