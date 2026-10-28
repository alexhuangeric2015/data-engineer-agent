s=new('建设定位与总体方向｜在既有平台上建设智能服务层','一、场景与价值')
# Positioning banner: enterprise place, HiAgent as runtime base, not a replacement platform.
surface(s,.48,1.18,12.36,.62,PALE,BORDER)
tx(s,.64,1.28,12.04,.44,'在既有数据平台之上建设智能服务层：以HiAgent为运行底座，配置专业能力与可信内容；不替代数仓、开发、调度与资产平台的权威与执行。',12.5,TITLE,True)

# Three boundary columns: reuse / build focus / target value.
for x,w,tag,title,sub,items,note,accent in [
    (.48,3.88,'复用','企业存量平台','权威事实与执行职责仍在原平台',
     [('数仓 / 计算引擎','业务数据与计算能力'),('开发 / 调度平台','代码发布与生产运行'),('数据资产平台','目录 · 指标 · 术语 · 血缘入口'),('运维 / 质量工具','运行事实与质量能力')],
     '现状：指标与术语已有，完整可靠待补强；血缘接口现为xlsx / 图',TEAL),
    (4.56,4.20,'建设重心','智能服务层','HiAgent是底座，不是建设终点',
     [('专业Agent','理解任务 · 规划步骤 · 协作核验'),('方法资产SKILL','企业经验进入工作步骤'),('可信内容载体','知识库 / 查询库 / 指标库 / 术语库'),('平台插件MCP','资产、运维与自建服务接入')],
     '当前切入：数据资产发现与解释（表字段 / 字典码值）',BLUE),
    (8.96,3.88,'目标方向','专业任务价值','三类九种，本页仅露出布局',
     [('数据生产 · 5种','需求 · 设计 · 开发 · 测试 · 评审'),('数据运营 · 3种','资产 · 运维 · 治理'),('数据分析 · 1种','受控计算与业务解释'),('演进关系','从资产查询 → 专业任务协作')],
     '完整九种角色详见能力地图专页',TITLE),
]:
    surface(s,x,1.98,w,3.92,WHITE,BORDER)
    box(s,x,2.12,.045,3.64,accent)
    strip(s,x+.22,2.12,1.28,tag,PALE if accent==BLUE else (MINT if accent==TEAL else SOFT),accent,11,h=.30)
    tx(s,x+.22,2.52,w-.40,.34,title,18,TITLE,True)
    tx(s,x+.22,2.88,w-.40,.28,sub,11,GRAY)
    for i,(a,b) in enumerate(items):
        yy=3.28+i*.52
        surface(s,x+.18,yy,w-.36,.46,SOFT,None)
        tx(s,x+.30,yy+.02,w-.60,.22,a,12.5,TITLE,True)
        tx(s,x+.30,yy+.22,w-.60,.20,b,10,GRAY)
    fill=SAND if accent==TEAL else (PALE if accent==BLUE else SOFT)
    surface(s,x+.18,5.42,w-.36,.36,fill,None)
    tx(s,x+.28,5.48,w-.56,.26,note,9.8,AMBER if accent==TEAL else (BLUE if accent==BLUE else TITLE))

# Overall direction is a first-class conclusion, not only a footer caption.
surface(s,.48,6.05,12.36,.48,DEEP,None)
tx(s,.64,6.10,1.30,.18,'总体方向',11,BLUE,True)
tx(s,10.70,6.10,1.90,.18,'治理机制另页',10,'93D9FF',align='right')
for i,(lab) in enumerate(['01 资产服务切入','02 可信内容与连接补强','03 研发专业协作','04 治理运维与分析扩展']):
    xx=.64+i*2.95
    strip(s,xx,6.30,2.55,lab,BLUE,WHITE,11,h=.18)
    if i<3:tx(s,xx+2.58,6.28,.30,.20,'→',14,'93D9FF',True,'center')

footer_band(s,'智能服务有效的前提是可信企业上下文；资产平台内容需治理确认后再进入HiAgent侧载体。',y=6.62)
n(s,'本页只讲定位、边界与方向。HiAgent是运行底座，建设重心是在其上配置Agent、SKILL、知识库、查询库、指标库、术语库与MCP插件。复用数仓、开发、调度与资产平台，原平台保留权威与执行。资产平台已有指标与术语，但完整可靠不足，且须导入HiAgent侧载体后Agent才有效。血缘现状为接口返回xlsx或图。总体方向：资产服务切入→可信内容与连接补强→研发协作→场景扩展。治理机制另页展开。')
