s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(WHITE)
manifest.append(dict(page=1,title='HiAgent企业数据智能体建设规划',section='封面'))
wave(s,True)
tx(s,.57,1.26,6.08,1.69,'企业数据智能体\n建设规划',39,TITLE,True)
box(s,.61,3.23,.72,.055,ORANGE)
tx(s,.61,3.72,5.63,.58,'夯实企业上下文，释放专业协作价值',21,INK,True)
for i,(kind,a,b) in enumerate([('data','数据可理解','资产与指标语义'),('flow','任务可协作','专业Agent与平台'),('chart','成果可验证','事实、证据与价值')]):
    xx=.61+i*1.87;iso(s,xx,4.69,.42,kind);tx(s,xx+.55,4.70,1.30,.28,a,11.5,TITLE,True);tx(s,xx+.55,5.11,1.30,.25,b,9.5,GRAY)
# Prominent native illustration, grounded in the actual platform relationships.
tx(s,6.72,.64,2.00,.30,'企业数据与知识',13,TITLE,True,'center')
tx(s,9.09,.64,2.13,.30,'HiAgent智能服务',13,TITLE,True,'center')
tx(s,11.44,.64,1.45,.30,'业务任务',13,TITLE,True,'center')
for yy,a,k in [(1.34,'资产与指标','data'),(2.92,'规范与方法','document'),(4.50,'平台事实','platform')]:
    surface(s,6.70,yy,1.79,1.19,WHITE,BORDER);iso(s,6.87,yy+.06,.67,k);tx(s,7.64,yy+.39,.78,.48,a,10.5,TITLE,True,'center')
iso(s,8.65,1.97,2.77,'platform')
tx(s,8.84,4.84,2.40,.44,'专业Agent协作',18,TITLE,True,'center')
tx(s,8.83,5.39,2.44,.47,'理解目标 · 规划任务\n按需调用 · 核验成果',11.5,GRAY,align='center')
for yy,a,k in [(1.34,'研发交付','code'),(2.92,'资产运营','data'),(4.50,'分析决策','chart')]:
    surface(s,11.53,yy,1.44,1.19,WHITE,BORDER);iso(s,11.91,yy+.08,.59,k);tx(s,11.67,yy+.80,1.16,.24,a,10.5,TITLE,True,'center')
for yy in [1.93,3.51,5.09]:
    route(s,[(8.54,yy),(8.72,yy),(8.72,3.60),(8.93,3.60)],BLUE)
    route(s,[(11.17,3.60),(11.35,3.60),(11.35,yy),(11.48,yy)],BLUE)
strip(s,7.23,6.14,5.44,'HiAgent × 企业上下文 × 既有平台',PALE,BLUE,13,h=.46)
tx(s,.61,6.46,5.8,.27,'规划汇报材料  /  架构视觉版 V7  /  2026年10月',10,GRAY)
n(s,'封面用原生立体示意连接企业内容、HiAgent与业务任务，不作为部署图或新的执行平台。只使用自制可编辑矢量，不复制参考中的品牌、数据或业务承诺。')
