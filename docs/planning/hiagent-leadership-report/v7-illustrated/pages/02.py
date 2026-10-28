s=new('建设定位与总体方向｜在既有平台上建设智能服务层','一、场景与价值')
# Left: data platform to reuse. Center: HiAgent service focus. Right: audiences and scenes.

surface(s,.38,1.12,3.05,5.28,WHITE,BORDER)
tx(s,.54,1.22,1.70,.28,'数据平台层',16,TITLE,True)
strip(s,2.35,1.22,.88,'复用',PALE,BLUE,11,h=.28)
line(s,.54,1.62,3.22,1.62,BORDER,.6)
for i,(title,body,kind) in enumerate([
    ('数仓与计算','业务数据与加工计算留在原平台','data'),
    ('开发与调度','模型、脚本、作业运行仍由原平台执行','code'),
    ('资产与元数据','目录、指标定义、术语与血缘入口','search'),
    ('质量与血缘','质量规则、血缘查询，不另建权威','flow'),
]):
    yy=1.76+i*.72
    surface(s,.54,yy,2.72,.64,SOFT,None)
    iso(s,.64,yy+.08,.40,kind)
    tx(s,1.16,yy+.06,1.98,.24,title,13,TITLE,True)
    tx(s,1.16,yy+.32,1.98,.24,body,10,GRAY)
surface(s,.54,4.72,2.72,1.50,'#F4F9FF',None)
box(s,.54,4.72,.045,1.50,ORANGE)
tx(s,.72,4.82,2.40,.24,'当前约束',13,TITLE,True)
for i,t in enumerate(['指标、术语已有，完整与可靠仍不足','血缘接口返回表格或图，图中才见脚本','口径权威与生产执行不迁出原平台']):
    tx(s,.72,5.16+i*.30,2.40,.26,'· '+t,10,INK)

surface(s,3.58,1.12,6.22,5.28,WHITE,BORDER)
tx(s,3.74,1.22,1.80,.28,'智能服务层',16,TITLE,True)
tx(s,5.50,1.24,1.50,.24,'本期建设重心',12,BLUE,True)
strip(s,8.05,1.22,1.55,'HiAgent是底座',PALE,BLUE,11,h=.28)
line(s,3.74,1.62,9.60,1.62,BORDER,.6)
surface(s,3.74,1.76,5.88,.62,BLUE,None)
tx(s,3.92,1.84,5.52,.26,'在HiAgent上配置能力与可信内容',15,WHITE,True)
tx(s,3.92,2.12,5.52,.20,'不新建数仓，不替代开发、调度与资产平台',11,'E4F0FF')
tx(s,3.74,2.48,1.40,.22,'专业能力',12,BLUE,True)
for i,(title,body,tag,kind) in enumerate([
    ('数据资产Agent','发现、解释、核验表字段与码值','当前','people'),
    ('按需协作','开发、分析、治理、运维按需引用','规划','code'),
    ('方法SKILL','规则进入步骤，由Agent调用资源','建设','document'),
]):
    xx=3.74+i*1.98
    surface(s,xx,2.74,1.90,.92,SOFT,None)
    iso(s,xx+.08,2.86,.36,kind)
    tx(s,xx+.50,2.82,1.32,.22,title,12,TITLE,True)
    tx(s,xx+.50,3.06,1.32,.20,tag,10,BLUE,True)
    tx(s,xx+.12,3.32,1.66,.26,body,10,GRAY)
tx(s,3.74,3.76,1.20,.22,'可信内容',12,BLUE,True)
tx(s,4.90,3.76,4.50,.22,'治理确认后进入HiAgent，Agent才真正可用',11,GRAY)
for i,(title,body,kind) in enumerate([
    ('知识库 / 查询库','表结构、字典码值：先定位，再核验','data'),
    ('指标库 / 术语库','承接资产平台已有定义，并补完整','chart'),
    ('MCP插件','连接资产、运维与自建服务','flow'),
]):
    xx=3.74+i*1.98
    surface(s,xx,4.04,1.90,.78,SOFT,None)
    iso(s,xx+.08,4.14,.34,kind)
    tx(s,xx+.50,4.12,1.32,.22,title,12,TITLE,True)
    tx(s,xx+.50,4.40,1.32,.32,body,10,GRAY)
surface(s,3.74,4.96,5.88,.70,PALE,None)
tx(s,3.88,5.02,1.20,.20,'工作方式',11,BLUE,True)
for i,lab in enumerate(['1 理解任务','2 规划步骤','3 引用知识与平台','4 核验后返回']):
    strip(s,3.88+i*1.45,5.30,1.28,lab,WHITE,TITLE,10,h=.26)
strip(s,4.55,5.78,4.20,'原平台保留权威与执行 · 智能服务组织任务',BLUE,WHITE,12,h=.32)
tx(s,3.74,6.16,5.88,.20,'治理闭环另页展开，本页不展开探查与确认机制',10,GRAY,align='center')

surface(s,9.96,1.12,2.98,5.28,WHITE,BORDER)
tx(s,10.12,1.22,2.60,.28,'服务对象与场景',16,TITLE,True)
line(s,10.12,1.62,12.74,1.62,BORDER,.6)
for i,(title,who,body,tag,kind) in enumerate([
    ('资产问答','业务、分析人员','定位资产、解释口径','当前','search'),
    ('研发协作','研发人员','看清来源、辅助设计与验证','规划','code'),
    ('运维与分析','运维、治理人员','异常取证、影响判断、口径消费','规划','chart'),
]):
    yy=1.78+i*.95
    surface(s,10.12,yy,2.66,.86,SOFT,None)
    iso(s,10.22,yy+.10,.36,kind)
    tx(s,10.68,yy+.08,1.20,.22,title,13,TITLE,True)
    tx(s,11.90,yy+.08,.78,.22,tag,11,BLUE,True,'right')
    tx(s,10.68,yy+.32,1.96,.20,who,11,BLUE)
    tx(s,10.68,yy+.54,1.96,.24,body,10,GRAY)
surface(s,10.12,4.70,2.66,1.52,PALE,None)
tx(s,10.26,4.80,2.38,.22,'当前就做这一件事',13,TITLE,True)
tx(s,10.26,5.06,2.38,.22,'数据资产发现与解释',12,BLUE,True)
for i,t in enumerate(['业务语言定位表、字段、码值','知识库取候选，查询库核验事实','缺失、冲突和权限限制要说清楚']):
    tx(s,10.26,5.36+i*.26,2.38,.24,'· '+t,10,INK)

surface(s,.38,6.52,12.56,.70,WHITE,BORDER)
tx(s,.54,6.56,1.50,.20,'总体方向',13,TITLE,True)
for i,(lab,body) in enumerate([
    ('01 资产问答切入','表字段与码值能够核对'),
    ('02 可信内容接入','治理结果进入知识、指标、术语库'),
    ('03 研发任务协作','限定链路形成验证证据'),
    ('04 场景继续扩展','运维取证与分析解释逐步放开'),
]):
    xx=.54+i*3.10
    tx(s,xx,6.78,2.70,.20,lab,12,TITLE,True)
    tx(s,xx,6.98,2.70,.18,body,10,GRAY)
    if i<3:tx(s,xx+2.72,6.82,.28,.22,'→',14,BLUE,True)

n(s,'本页保持左平台、中服务、右场景、底方向。HiAgent是运行底座。当前只建设数据资产Agent，其他专业Agent为规划，不单列协调器。SKILL提供方法，由Agent调用资源。指标与术语需治理确认后进入HiAgent指标库和术语库。血缘现状为表格或图。客户架构图只借鉴分层，不移植NL2SQL等名称作为已建设能力。')
