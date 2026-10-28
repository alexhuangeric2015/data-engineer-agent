# Illustration-led native architecture system, grounded in the supplied reference.
BLUE='116FE8';TITLE='082850';DEEP='082850';PALE='EAF5FF';SOFT='F5FAFF';BORDER='D4E7FA';GRAY='546D89';INK='173556';TEAL='078B9F';MINT='EAF9FA';ORANGE='EE8B24';AMBER='BD741F';SAND='FFF6E9'

def poly(s,pts,fill,stroke=None,width=.6):
    pts=[(int(x*914400),int(y*914400)) for x,y in pts]
    b=s.shapes.build_freeform(pts[0][0],pts[0][1]);b.add_line_segments(pts[1:],close=True);a=b.convert_to_shape()
    a.fill.solid();a.fill.fore_color.rgb=rgb(fill)
    if stroke:a.line.color.rgb=rgb(stroke);a.line.width=Pt(width)
    else:a.line.fill.background()
    clean(a);return a

def ellipse(s,x,y,w,h,col,stroke=None):
    a=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(w),Inches(h));a.fill.solid();a.fill.fore_color.rgb=rgb(col)
    if stroke:a.line.color.rgb=rgb(stroke);a.line.width=Pt(.6)
    else:a.line.fill.background()
    clean(a);return a

def cube(s,x,y,w,h,depth=None,top='93D9FF',left='1D8FF0',right='0B5EC9'):
    d=depth or w*.23
    poly(s,[(x,y+d),(x+w/2,y),(x+w,y+d),(x+w/2,y+2*d)],top)
    poly(s,[(x,y+d),(x+w/2,y+2*d),(x+w/2,y+2*d+h),(x,y+d+h)],left)
    poly(s,[(x+w/2,y+2*d),(x+w,y+d),(x+w,y+d+h),(x+w/2,y+2*d+h)],right)

def iso(s,x,y,d=1.0,kind='platform'):
    # All icon faces are native editable geometry. The pale ellipse anchors the object.
    ellipse(s,x+.07*d,y+.83*d,.90*d,.16*d,'DDEFFF')
    if kind in ['platform','flow','layers']:
        for i,ww in enumerate([.92,.76,.58]):cube(s,x+(.98-ww)/2*d,y+(.56-i*.19)*d,ww*d,.085*d,ww*.21*d,['B8E8FF','94D7FF','57BEFF'][i],['6DC8FF','3FAAFF','148CEB'][i],['308FE8','1972D4','0A54BE'][i])
        for xx,yy in [(.34,.14),(.59,.23),(.43,.35)]:cube(s,x+xx*d,y+yy*d,.19*d,.14*d,top='ACECFF',left='31B9F5',right='1665CC')
    elif kind=='data':
        xx=x+.21*d;yy=y+.12*d;ww=.61*d;hh=.70*d
        box(s,xx,yy+.10*d,ww,hh-.12*d,'168EEC')
        ellipse(s,xx,yy+.60*d,ww,.20*d,'0967C9')
        for k in [0,.23,.46]:ellipse(s,xx,yy+k*d,ww,.20*d,'76D8FF' if k==0 else '3AB2F8','C6EDFF')
        # Left light highlight.
        box(s,xx+.06*d,yy+.12*d,.04*d,.53*d,'76D1FF')
    elif kind in ['chart','value']:
        cube(s,x+.08*d,y+.69*d,.87*d,.04*d,top='BFEAFF',left='7FCBFD',right='5AA7EC')
        for i,(yy,hh) in enumerate([(.56,.18),(.37,.37),(.12,.62)]):cube(s,x+(.15+i*.24)*d,y+yy*d,.19*d,hh*d,.04*d,'92E5FF','2AB5F8','1168CE')
    elif kind in ['code','document','check','search']:
        # Extruded upright document, with perspective and pale lines.
        poly(s,[(x+.20*d,y+.13*d),(x+.72*d,y+.06*d),(x+.84*d,y+.15*d),(x+.32*d,y+.23*d)],'B1E8FF')
        poly(s,[(x+.72*d,y+.06*d),(x+.84*d,y+.15*d),(x+.84*d,y+.77*d),(x+.72*d,y+.70*d)],'1474DB')
        poly(s,[(x+.20*d,y+.13*d),(x+.72*d,y+.06*d),(x+.72*d,y+.70*d),(x+.20*d,y+.78*d)],'52B9F6')
        for k in range(3):line(s,x+.29*d,y+(.31+k*.14)*d,x+.62*d,y+(.26+k*.14)*d,'ECFAFF',1.2)
        if kind=='code':
            tx(s,x+.25*d,y+.40*d,.43*d,.21*d,'</>',max(8,16*d),WHITE,True,'center')
        elif kind=='check':
            line(s,x+.34*d,y+.47*d,x+.44*d,y+.57*d,WHITE,2);line(s,x+.44*d,y+.57*d,x+.64*d,y+.33*d,WHITE,2)
    elif kind=='people':
        ellipse(s,x+.39*d,y+.10*d,.24*d,.24*d,'3BAAF4')
        poly(s,[(x+.27*d,y+.46*d),(x+.51*d,y+.33*d),(x+.76*d,y+.47*d),(x+.76*d,y+.77*d),(x+.27*d,y+.77*d)],'1E8CE5')
    else:
        a=s.shapes.add_shape(MSO_SHAPE.GEAR_6,Inches(x+.17*d),Inches(y+.17*d),Inches(.67*d),Inches(.67*d));a.fill.solid();a.fill.fore_color.rgb=rgb('198BF0');a.line.fill.background();clean(a);ellipse(s,x+.40*d,y+.40*d,.21*d,.21*d,'E6F7FF')

def icon(s,x,y,kind='data',c=None,d=.36):iso(s,x,y,d,kind)

def wave(s,cover=False):
    # Light technical landscape; decorative only and fully editable.
    base=6.55 if cover else 7.08
    for k in range(11 if cover else 5):
        pts=[]
        for j in range(91):
            xx=j*13.333/90;yy=base+k*.065+.11*math.sin(xx*.83+k*.23)+(.14 if cover else .03)*math.sin(xx*1.8)
            pts.append((xx,min(7.48,yy)))
        # Open native freeform with a light stroke.
        q=[(int(a*914400),int(b*914400)) for a,b in pts];b=s.shapes.build_freeform(q[0][0],q[0][1]);b.add_line_segments(q[1:],close=False);a=b.convert_to_shape();a.fill.background();a.line.color.rgb=rgb('E5F2FD' if k%2 else 'DDEDFB');a.line.width=Pt(.6);clean(a)
    if cover:
        for i,hh in enumerate([.35,.70,.48,.93,.62,1.16]):box(s,11.07+i*.28,7.18-hh,.15,hh,'E5F1FB')

def header(s,title,section):
    kind,sep,claim=title.partition('｜')
    tx(s,.46,.16,12.34,.49,kind if sep else title,27,TITLE,True)
    box(s,.48,.79,.64,.045,ORANGE)
    tx(s,1.30,.71,11.45,.27,claim if sep else section,13.2,INK)
    tx(s,11.82,.32,.98,.22,'HiAgent',9,BLUE,True,'right')
    tx(s,.49,7.27,11.2,.14,'企业数据智能体建设规划  /  规划视图  /  2026.10',7.3,GRAY)
    tx(s,12.15,7.25,.64,.19,f'{len(prs.slides):02d}',9,TITLE,True,'right')

def new(title,section,summary=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]);s.background.fill.solid();s.background.fill.fore_color.rgb=rgb(WHITE)
    wave(s);header(s,title,section)
    if summary:tx(s,.49,1.24,12.27,.29,summary,11.7,GRAY)
    manifest.append(dict(page=len(prs.slides),title=title,section=section));return s

def surface(s,x,y,w,h,fill=WHITE,stroke=None):
    if fill not in [DEEP,TITLE,'082850']:
        box(s,x+.025,y+.035,w,h,'EAF3FC',None,r=.06)
    return box(s,x,y,w,h,fill,stroke or BORDER,r=.055)

def node(s,x,y,w,h,title,body='',accent=None,fill=None,sz=16,bs=14):
    accent=accent or BLUE;fill=fill or WHITE;surface(s,x,y,w,h,fill,BORDER)
    if h>=1.45 and w>=2.55:
        iso(s,x+.15,y+.15,.57,kindof(title));tx(s,x+.85,y+.19,w-1.02,.43,title,min(sz,17),TITLE,True)
        by=.88 if h<1.65 else .99
        if body:tx(s,x+.23,y+by,w-.46,h-by-.08,body,min(bs,14),INK,top=True)
    else:
        box(s,x+.16,y+.16,.035,.23,BLUE)
        tx(s,x+.28,y+.09,w-.43,.42,title,min(sz,15.5),TITLE,True)
        if body:tx(s,x+.20,y+.61,w-.40,max(.23,h-.72),body,min(bs,13),GRAY)
    return (x,y,w,h)

def lane(s,x,w,title,fill=None,y=1.77,h=4.54):
    surface(s,x,y,w,h,fill or SOFT,BORDER)
    tx(s,x+.18,y+.13,w-.36,.34,title,15,TITLE,True)
    line(s,x+.18,y+.58,x+w-.18,y+.58,BORDER,.7)

def footer_band(s,t,y=6.65):
    surface(s,.48,y,12.30,.37,'EEF7FF',None)
    tx(s,.64,y+.04,11.98,.27,t,10.5,INK)

def showcase(s,x,y,w,h,title,body,kind='platform',c=BLUE):
    surface(s,x,y,w,h,WHITE,BORDER);iso(s,x+(w-1.14)/2,y+.45,1.14,kind)
    tx(s,x+.15,y+.12,w-.30,.32,title,15,c,True,'center')
    tx(s,x+.18,y+1.80,w-.36,h-1.94,body,12.5,INK,align='center')

def scenario_map(s,steps,problems,values):
    total=9.15;gap=.20;cw=(total-gap*(len(steps)-1))/len(steps)
    for i,(title,kind,datum,body) in enumerate(steps):
        xx=.55+i*(cw+gap);surface(s,xx,1.81,cw,4.31,WHITE,BORDER)
        tx(s,xx+.13,2.02,cw-.26,.26,f'{i+1:02d}',11,BLUE,True)
        tx(s,xx+.13,2.44,cw-.26,.40,title,15 if len(steps)<5 else 13.5,TITLE,True)
        d=min(1.07,cw-.30);iso(s,xx+(cw-d)/2,3.04,d,kind)
        strip(s,xx+.12,4.45,cw-.24,datum,PALE,INK,10.5,h=.47)
        tx(s,xx+.14,5.20,cw-.28,.64,body,11.3,GRAY,align='center')
        if i<len(steps)-1:arrow(s,xx+cw+.025,3.58,xx+cw+gap-.025,3.58,BLUE,1.5)
    xx=10.03;ww=2.74
    for yy,title,items,c in [(1.81,'解决问题',problems,BLUE),(4.05,'应用价值',values,TEAL)]:
        surface(s,xx,yy,ww,2.07,WHITE,BORDER);box(s,xx+.17,yy+.15,.035,.27,ORANGE)
        tx(s,xx+.33,yy+.13,ww-.49,.34,title,17,TITLE,True)
        for j,(a,b) in enumerate(items):
            tx(s,xx+.21,yy+.72+j*.62,ww-.42,.25,a,12,c,True)
            tx(s,xx+.21,yy+1.04+j*.62,ww-.42,.23,b,9.8,GRAY)
