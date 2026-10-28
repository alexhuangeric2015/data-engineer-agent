s=new('建设定位与总体方向｜从资产查询走向专业任务协作','一、场景与价值')
# Central architecture hero, with clearly named input and output groups.
for y,a,b,k in [(1.62,'数据资产','表字段 / 字典码值 / 指标','data'),(3.13,'企业知识','规范 / 模板 / SKILL','document'),(4.64,'平台能力','开发 / 调度 / 血缘 / 质量','platform')]:
    surface(s,.55,y,3.12,1.23,WHITE,BORDER);iso(s,.71,y+.13,.67,k);tx(s,1.55,y+.18,1.90,.35,a,17,TITLE,True);tx(s,1.55,y+.71,1.90,.33,b,10.3,GRAY)
iso(s,4.25,1.88,3.49,'platform')
tx(s,4.36,5.29,3.29,.45,'HiAgent专业智能服务',21,TITLE,True,'center')
tx(s,4.36,5.83,3.29,.34,'Agent组织任务，企业上下文约束判断',10.5,GRAY,align='center')
for y,a,b,k in [(1.62,'数据生产','复用需求、辅助设计、开发与验证','code'),(3.13,'数据运营','发现资产、理解口径、组织异常证据','data'),(4.64,'数据分析','受控计算、多维分析与业务解释','chart')]:
    surface(s,9.15,y,3.62,1.23,WHITE,BORDER);iso(s,9.31,y+.13,.67,k);tx(s,10.17,y+.18,2.36,.35,a,17,TITLE,True);tx(s,10.17,y+.71,2.36,.33,b,10.3,GRAY)
for yy in [2.23,3.74,5.25]:
    route(s,[(3.72,yy),(3.96,yy),(3.96,3.78),(4.34,3.78)],BLUE)
    route(s,[(7.63,3.78),(8.51,3.78),(8.51,yy),(9.10,yy)],BLUE)
footer_band(s,'当前以资产智能体切入；企业内容、平台连接与专业场景逐步扩展，原平台保留权威与执行职责。')
n(s,'总体方向不改变当前只建设资产Agent的范围。中心为智能服务不是新建数仓，左右分别是内容和平台能力输入、目标业务服务。角色布局保留三类九种。')
