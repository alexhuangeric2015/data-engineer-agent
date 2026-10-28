s=new('建设定位与总体方向｜在既有平台上建设智能服务层','一、场景与价值')
# Layout mirrors reference scenario pages: left reuse / center build focus / right value / bottom direction.

# LEFT — enterprise platforms to reuse, with current constraints.
surface(s,.42,1.14,2.95,5.20,WHITE,BORDER)
surface(s,.42,1.14,2.95,.42,PALE,None)
tx(s,.58,1.20,1.70,.30,'企业存量平台',16,TITLE,True)
strip(s,2.45,1.20,.75,'复用',MINT,TEAL,11,h=.28)
box(s,.42,1.56,.045,4.78,TEAL)
for i,(title,body,kind) in enumerate([
    ('数仓 / 计算引擎','业务数据与计算能力保留','data'),
    ('开发 / 调度平台','代码发布与生产运行保留','code'),
    ('数据资产平台','目录 · 指标 · 术语 · 血缘入口','search'),
    ('运维 / 质量工具','运行事实与质量能力保留','platform'),
]):
    yy=1.70+i*.72
    surface(s,.58,yy,2.62,.64,SOFT,None)
    iso(s,.68,yy+.05,.42,kind)
    tx(s,1.20,yy+.08,1.88,.24,title,12.5,TITLE,True)
    tx(s,1.20,yy+.34,1.88,.24,body,10,GRAY)
surface(s,.58,4.70,2.62,1.48,SAND,None)
tx(s,.72,4.80,2.30,.24,'当前约束',13,AMBER,True)
for i,t in enumerate(['指标 / 术语已有，完整可靠不足','血缘接口为xlsx或图，图中才见脚本','权威与执行仍归属原平台责任方']):
    tx(s,.72,5.16+i*.28,2.30,.26,'· '+t,10,INK)

# CENTER — HiAgent as runtime base and configuration focus.
surface(s,3.55,1.14,6.55,5.20,WHITE,BORDER)
surface(s,3.55,1.14,6.55,.42,PALE,None)
tx(s,3.72,1.20,3.80,.30,'智能服务层 · 本期建设重心',16,TITLE,True)
tx(s,7.55,1.22,2.35,.26,'HiAgent是底座，不是终点',11,BLUE,True,'right')
surface(s,3.72,1.70,6.20,.58,DEEP,None)
iso(s,3.86,1.76,.42,'platform')
tx(s,4.40,1.76,5.30,.24,'HiAgent运行底座',15,WHITE,True)
tx(s,4.40,2.02,5.30,.20,'配置Agent、SKILL、知识与库、插件；组织专业任务并引用平台事实',10.5,'B9DAFF')
for i,(title,body,kind) in enumerate([
    ('专业Agent','理解 · 规划 · 协作核验','people'),
    ('方法SKILL','规则与经验进入步骤','document'),
    ('知识 / 查询库','候选定位 + 事实核验','data'),
    ('指标 / 术语库','口径与业务语言','chart'),
    ('MCP插件','资产 / 运维 / 自建服务','flow'),
    ('权限与证据','身份、确认与可追溯','check'),
]):
    xx=3.72+(i%3)*2.10; yy=2.46+(i//3)*.95
    surface(s,xx,yy,1.98,.84,SOFT,None)
    iso(s,xx+.10,yy+.12,.42,kind)
    tx(s,xx+.60,yy+.14,1.26,.26,title,12.5,TITLE,True)
    tx(s,xx+.60,yy+.46,1.26,.28,body,10,GRAY)
surface(s,3.72,4.46,6.20,.78,PALE,None)
tx(s,3.88,4.52,1.20,.22,'工作机制',11,BLUE,True)
for i,lab in enumerate(['01 理解目标','02 规划任务','03 引用资源','04 核验返回']):
    xx=3.88+i*1.52
    strip(s,xx,4.82,1.30,lab,WHITE,TITLE,10.5,h=.28)
    if i<3:tx(s,xx+1.32,4.80,.18,.28,'→',14,BLUE,True,'center')
strip(s,4.70,5.40,4.20,'企业上下文约束判断 · 原平台保留权威执行',BLUE,WHITE,12,h=.36)
tx(s,3.72,5.88,6.20,.28,'先治理确认，再进入HiAgent可消费载体；治理机制另页展开',10,GRAY,align='center')

# RIGHT — professional task value and current entry example.
surface(s,10.28,1.14,2.68,5.20,WHITE,BORDER)
surface(s,10.28,1.14,2.68,.42,SOFT,None)
tx(s,10.44,1.20,1.70,.30,'专业任务价值',16,TITLE,True)
strip(s,12.10,1.20,.68,'目标',PALE,BLUE,11,h=.28)
box(s,12.91,1.56,.05,4.78,BLUE)
for i,(title,body,value,kind) in enumerate([
    ('生产类','需求 / 设计 / 开发 / 测试 / 评审','缩短交付链路','code'),
    ('运营类','资产发现 / 运维诊断 / 治理闭环','提高可靠与闭环','search'),
    ('分析类','受控计算 / 多维分析 / 业务解释','统一口径决策','chart'),
]):
    yy=1.70+i*.92
    surface(s,10.44,yy,2.36,.82,SOFT,None)
    iso(s,10.54,yy+.08,.38,kind)
    tx(s,11.00,yy+.08,1.68,.24,title,13,TITLE,True)
    tx(s,11.00,yy+.34,1.68,.22,body,9.5,GRAY)
    tx(s,10.54,yy+.56,2.10,.20,value,11,BLUE,True)
surface(s,10.44,4.55,2.36,1.63,PALE,None)
tx(s,10.58,4.64,2.08,.24,'当前切入示例',13,TITLE,True)
tx(s,10.58,4.94,2.08,.22,'数据资产发现与解释',11.5,BLUE,True)
for i,t in enumerate(['业务语言定位候选资产','外部库核验表字段 / 码值','连续追问与相关建议']):
    tx(s,10.58,5.28+i*.26,2.08,.24,'· '+t,10,INK)

# Connector labels between columns.
tx(s,3.35,2.55,.22,.50,'能力\n引用',9,BLUE,True,'center')
tx(s,10.05,2.55,.22,.50,'任务\n赋能',9,BLUE,True,'center')

# BOTTOM — overall direction as first-class conclusion.
surface(s,.42,6.48,12.54,0.72,WHITE,BORDER)
tx(s,.58,6.54,1.40,.22,'总体方向',14,TITLE,True)
tx(s,10.80,6.54,2.00,.20,'治理专页另述',10,GRAY,align='right')
for i,(lab,body,kind) in enumerate([
    ('01 资产服务切入','表字段 / 字典码值可核对','search'),
    ('02 可信内容与连接','治理确认后进入HiAgent载体','check'),
    ('03 研发专业协作','需求到验证证据成闭环','code'),
    ('04 场景扩展','治理运维与分析持续回归','chart'),
]):
    xx=.58+i*3.10
    iso(s,xx,6.78,.28,kind)
    tx(s,xx+.36,6.76,2.40,.22,lab,12,TITLE,True)
    tx(s,xx+.36,6.98,2.40,.18,body,9.5,GRAY)
    if i<3:tx(s,xx+2.78,6.84,.24,.24,'→',14,BLUE,True,'center')

n(s,'本页只讲定位、边界与方向。HiAgent是运行底座，建设重心是在其上配置Agent、SKILL、知识库、查询库、指标库、术语库与MCP插件。复用数仓、开发、调度与资产平台，原平台保留权威与执行。资产平台已有指标与术语，但完整可靠不足，且须导入HiAgent侧载体后Agent才有效。血缘现状为接口返回xlsx或图。总体方向：资产服务切入→可信内容与连接补强→研发协作→场景扩展。治理机制另页展开。')
