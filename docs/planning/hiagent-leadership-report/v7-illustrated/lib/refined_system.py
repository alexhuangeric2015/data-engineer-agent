# Refined consulting visual system. All primitives remain editable.
BLUE='245BA8';TITLE='163E6B';DEEP='123861';PALE='EFF4FB';SOFT='F7F9FC';BORDER='DDE5EF'
INK='26364A';GRAY='65758B';TEAL='13857C';MINT='EDF7F4';AMBER='A77B42';SAND='FBF5EB'
SECTION_EN={'一、场景与价值':'01  SCENARIOS & VALUE','二、能力与系统架构':'02  CAPABILITIES & ARCHITECTURE','三、核心模块与建设价值':'03  ENTERPRISE FOUNDATIONS','四、数据与协作原理':'04  DATA & COLLABORATION','五、场景赋能与建设路径':'05  BUSINESS ENABLEMENT','六、部署与建设演进':'06  DEPLOYMENT & EVOLUTION','公开依据':'REFERENCES'}
# Retain existing source data but use more legible headings and subdued connections.
_tx=tx
_original_arrow=arrow
def arrow(s,x1,y1,x2,y2,c='7895B4',width=1.0):
    return _original_arrow(s,x1,y1,x2,y2,c,width)

def tx(s,x,y,w,h,t,size=15,c=None,bold=False,align='left',top=False,link=None):
    a=_tx(s,x,y,w,h,t,size,c or INK,bold,align,top,link)
    if link:
        for p in a.text_frame.paragraphs:
            for r in p.runs:r.font.color.rgb=rgb(c or INK);r.font.underline=False
    return a

def header(s,title,section):
    kind,sep,claim=title.partition('｜')
    tx(s,.48,.16,10.3,.23,SECTION_EN.get(section,section)+'  /  '+kind,8.5,GRAY,True)
    tx(s,.48,.47,12.37,.43,claim if sep else title,24,TITLE,True)
    # Small typographic identifier, no imitation client logo.
    tx(s,11.13,.16,1.72,.23,'HiAgent  /  DATA',9,BLUE,True,'right')
    line(s,.48,.995,12.85,.995,BORDER,.65)
    box(s,.48,.995,.58,.025,BLUE)
    line(s,.48,7.19,12.85,7.19,BORDER,.55)
    tx(s,.48,7.27,10,.14,'企业数据智能体建设规划  /  规划汇报  /  2026.10',7.5,GRAY)
    tx(s,11.82,7.24,1.03,.22,f'{len(prs.slides):02d}  /  30',9,TITLE,True,'right')

def new(title,section,summary=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(WHITE)
    header(s,title,section)
    if summary:
        box(s,.48,1.07,.035,.40,TEAL)
        tx(s,.64,1.075,12.14,.37,summary,12.8,GRAY)
    manifest.append(dict(page=len(prs.slides),title=title,section=section));return s

def footer_band(s,t,y=6.65):
    box(s,.48,y,12.37,.39,SOFT)
    tx(s,.63,y+.035,.77,.28,'规划要点',9.5,BLUE,True)
    tx(s,1.45,y+.025,11.22,.31,t,11.5,INK)

def icon(s,x,y,kind='data',c=BLUE,d=.36):
    # Restrained line icon set, purpose-specific and constructed from native shapes.
    def L(a,b,e,f):line(s,x+a*d,y+b*d,x+e*d,y+f*d,c,.9)
    if kind=='data':
        box(s,x+.10*d,y+.14*d,.8*d,.72*d,WHITE,c,r=.025)
        for a in [.36,.58]:L(.12,a,.88,a)
        L(.35,.18,.35,.82)
    elif kind=='layers':
        for k in range(3):
            yy=.15+k*.25;L(.1,yy,.9,yy);L(.1,yy,.1,yy+.12);L(.1,yy+.12,.9,yy+.12)
    elif kind=='code':
        L(.32,.25,.1,.5);L(.1,.5,.32,.75);L(.68,.25,.9,.5);L(.9,.5,.68,.75);L(.58,.15,.43,.85)
    elif kind=='check':
        box(s,x+.1*d,y+.1*d,.8*d,.8*d,WHITE,c,r=.05);L(.26,.51,.43,.69);L(.43,.69,.77,.30)
    elif kind=='chart':
        L(.12,.10,.12,.9);L(.12,.9,.95,.9)
        for xx,hh in [(.27,.25),(.5,.5),(.73,.72)]:box(s,x+xx*d,y+(.84-hh)*d,.13*d,hh*d,c)
    elif kind=='search':
        circle(s,x+.08*d,y+.06*d,.56*d,WHITE,c);L(.57,.59,.91,.94)
    elif kind=='people':
        circle(s,x+.36*d,y+.07*d,.28*d,WHITE,c);L(.2,.88,.2,.63);L(.2,.63,.5,.46);L(.5,.46,.8,.63);L(.8,.63,.8,.88);L(.2,.88,.8,.88)
    elif kind=='flow':
        for a,b in [(.08,.14),(.65,.14),(.36,.68)]:box(s,x+a*d,y+b*d,.28*d,.20*d,WHITE,c,r=.03)
        L(.36,.24,.65,.24);L(.78,.34,.78,.53);L(.78,.53,.5,.53);L(.5,.53,.5,.68)
    else:
        box(s,x+.12*d,y+.05*d,.76*d,.90*d,WHITE,c,r=.02)
        for yy in [.29,.48,.67]:L(.27,yy,.73,yy)

def kindof(t):
    if any(w in t for w in ['数据','资产','事实','码值','字段','索引']):return 'data'
    if any(w in t for w in ['测试','审核','确认','验证','规则','评审']):return 'check'
    if any(w in t for w in ['开发','代码','SQL']):return 'code'
    if any(w in t for w in ['分析','指标','收益','成果']):return 'chart'
    if any(w in t for w in ['用户','责任','人员','专家']):return 'people'
    if any(w in t for w in ['Agent','任务','平台','集成','调用','服务']):return 'flow'
    if any(w in t for w in ['检索','查找','发现']):return 'search'
    return 'layers'

def node(s,x,y,w,h,title,body='',accent=None,fill=None,sz=16,bs=14):
    accent=accent or BLUE;fill=fill or WHITE
    box(s,x,y,w,h,fill,BORDER,r=.035)
    if h>=1.45 and w>=2.55:
        icon(s,x+.19,y+.20,kindof(title),accent,.33)
        tx(s,x+.67,y+.14,w-.86,.43,title,min(sz,18),TITLE,True)
        compact=h<1.65;yy=.70 if compact else .77;by=.81 if compact else .89
        line(s,x+.20,y+yy,x+w-.20,y+yy,BORDER,.6)
        if body:tx(s,x+.23,y+by,w-.46,h-by-.10,body,bs,INK,top=True)
    else:
        # Compact modules read as one labeled object, rather than a miniature slide.
        box(s,x+.15,y+.16,.045,.26,accent,r=.02)
        tx(s,x+.27,y+.09,w-.42,.43,title,min(sz,16),TITLE,True)
        if body:tx(s,x+.20,y+.62,w-.40,max(.22,h-.73),body,bs,GRAY,align='left')
    return (x,y,w,h)

def strip(s,x,y,w,t,fill=None,c=None,sz=14,h=.48):
    fill=fill or PALE;c=c or DEEP
    box(s,x,y,w,h,fill,None,r=.035)
    tx(s,x+.10,y+.035,w-.20,h-.07,t,sz,c,True,'center')

def lane(s,x,w,title,fill=None,y=1.77,h=4.54):
    fill=fill or SOFT
    box(s,x,y,w,h,fill,None,r=.035)
    # The header is part of the region, not another heavy blue slab.
    tx(s,x+.19,y+.11,w-.38,.32,title,14.5,TITLE,True)
    line(s,x+.19,y+.55,x+w-.19,y+.55,BORDER,.8)

def seq(s,items,y=2.10,h=1.9,x=.45,total=12.43,gap=.32):
    w=(total-gap*(len(items)-1))/len(items);arr=[]
    for i,(a,b) in enumerate(items):
        xx=x+i*(w+gap)
        arr.append(node(s,xx,y,w,h,a,b,sz=17,bs=14))
        circle(s,xx+.17,y-.14,.30,BLUE);tx(s,xx+.17,y-.115,.30,.23,f'{i+1:02}',9,WHITE,True,'center')
        if i<len(items)-1:arrow(s,xx+w+.04,y+h/2,xx+w+gap-.04,y+h/2,'7895B4',.95)
    return arr

def route(s,pts,c=None,label=None,at=None):
    c=c or '7895B4'
    # Drop zero-length segments and merge collinear segments for clear edits.
    pp=[]
    for p in pts:
        if not pp or p!=pp[-1]:pp.append(p)
    if len(pp)<2:return
    for a,b in zip(pp[:-2],pp[1:-1]):line(s,*a,*b,c,.95)
    arrow(s,*pp[-2],*pp[-1],c,.95)
    if label and at:
        x,y,w,h=at;box(s,x,y,w,h,WHITE);tx(s,x+.02,y+.01,w-.04,h-.02,label,11,GRAY,align='center')

def tag(s,x,y,w,text,c=BLUE):
    box(s,x,y,w,.27,PALE if c==BLUE else MINT);tx(s,x+.05,y+.02,w-.1,.23,text,8.5,c,True,'center')

def surface(s,x,y,w,h,fill=SOFT,stroke=None):return box(s,x,y,w,h,fill,stroke,r=.045)

def db(s,x,y,w,h,title,body,c=BLUE):
    # Flat cylinder rendered with editable rectangle and ellipses.
    eh=.19
    box(s,x,y+eh/2,w,h-eh,WHITE,c)
    a=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y+h-eh),Inches(w),Inches(eh));a.fill.solid();a.fill.fore_color.rgb=rgb(WHITE);a.line.color.rgb=rgb(c);a.line.width=Pt(.65);clean(a)
    a=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(w),Inches(eh));a.fill.solid();a.fill.fore_color.rgb=rgb(PALE if c==BLUE else MINT);a.line.color.rgb=rgb(c);a.line.width=Pt(.65);clean(a)
    if h<1.2:
        tx(s,x+.16,y+.22,w-.32,.29,title,14,TITLE,True,'center')
        tx(s,x+.17,y+.62,w-.34,.22,body,10.5,GRAY,align='center')
    else:
        tx(s,x+.16,y+.25,w-.32,.36,title,16,TITLE,True,'center')
        tx(s,x+.17,y+.77,w-.34,h-.96,body,13,GRAY,align='center')
