#!/usr/bin/env python3
"""Render 20 pitch slides (1920x1080) in the ControlPlane design language.
Tokens lifted from ../../../../design-system2/tailwind-preset.cjs (the real brand theme).
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib, math

HERE = pathlib.Path(__file__).parent
OUT = HERE/"slides"; OUT.mkdir(exist_ok=True)
F = HERE/"assets"/"fonts"
W, H = 1920, 1080
MARGIN = 130

# --- palette (ControlPlane brand) ---
BG      = (15,15,15)     # #0f0f0f
DARKER  = (10,10,10)     # #0a0a0a
CARD    = (20,20,20)     # #141414
CARD2   = (23,24,26)     # #17181a
BLUE    = (28,100,242)   # #1c64f2 brand
BLUE_DK = (18,64,150)
WHITE   = (250,252,255)  # #fafcff headings
BODY    = (215,220,224)  # #d7dce0
MUTED   = (163,163,163)  # #a3a3a3
NEUT6   = (113,118,122)  # #71767a
PILL    = (31,31,31)     # #1f1f1f
AMBER   = (224,165,61)   # Audit
RED     = (229,72,77)    # Deny
GREEN   = (63,185,127)   # verified/pass
LINE    = (38,39,41)     # #262729 hairlines

def font(name, size):
    return ImageFont.truetype(str(F/name), size)
def bebas(s):  return font("BebasNeue-Regular.ttf", s)
def mb(s):     return font("Montserrat-Bold.otf", s)
def mr(s):     return font("Montserrat-Regular.otf", s)
def mono(s):   return ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", s)

def tw(d,t,f): return d.textlength(t,font=f)
def th(f):
    a=f.getbbox("Hg"); return a[3]-a[1]

def wrap(d,t,f,maxw):
    words=t.split(); lines=[]; cur=""
    for w_ in words:
        test=(cur+" "+w_).strip()
        if tw(d,test,f)<=maxw: cur=test
        else: lines.append(cur); cur=w_
    if cur: lines.append(cur)
    return lines

def rrect(d,box,r,fill=None,outline=None,width=1):
    d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def base(idx):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    # subtle top vignette band
    d.rectangle([0,0,W,6],fill=BLUE)
    # footer chrome
    fy=H-70
    d.line([MARGIN,fy,W-MARGIN,fy],fill=LINE,width=2)
    d.text((MARGIN,fy+18),"POLICY  AS  VERSIONED  FLUX",font=mb(20),fill=NEUT6)
    num=f"{idx:02d} / 20"
    d.text((W-MARGIN-tw(d,num,mb(20)),fy+18),num,font=mb(20),fill=MUTED)
    # progress ticks
    seg=(W-2*MARGIN)/20; py=H-34
    for i in range(20):
        x0=MARGIN+i*seg+3; x1=MARGIN+(i+1)*seg-3
        d.line([x0,py,x1,py],fill=(BLUE if i<idx else LINE),width=4)
    # brand mark top-left
    d.rectangle([MARGIN,MARGIN-46,MARGIN+10,MARGIN-16],fill=BLUE)
    d.text((MARGIN+24,MARGIN-52),"ControlPlane",font=mb(26),fill=WHITE)
    return img,d

def eyebrow(d,y,text,color=BLUE):
    d.rectangle([MARGIN,y+4,MARGIN+46,y+10],fill=color)
    d.text((MARGIN+62,y-8),text.upper(),font=mb(26),fill=color)
    return y+34

def title(d,y,text,size=150,color=WHITE,maxw=W-2*MARGIN,accent=None,lh=0.92):
    f=bebas(size); lines=wrap(d,text.upper(),f,maxw)
    for ln in lines:
        x=MARGIN
        if accent:
            # colour any word in `accent` set blue
            words=ln.split(" ")
            for wd in words:
                col=BLUE if wd.strip(",.").upper() in accent else color
                d.text((x,y),wd,font=f,fill=col); x+=tw(d,wd+" ",f)
        else:
            d.text((MARGIN,y),ln,font=f,fill=color)
        y+=int(size*lh)
    return y

def body(d,y,text,size=34,color=BODY,maxw=W-2*MARGIN,x=MARGIN):
    f=mr(size)
    for ln in wrap(d,text,f,maxw):
        d.text((x,y),ln,font=f,fill=color); y+=int(size*1.4)
    return y

def check(d,cx,cy,s,color=GREEN,w=7):
    d.line([(cx-s*0.5,cy),(cx-s*0.1,cy+s*0.45),(cx+s*0.6,cy-s*0.5)],fill=color,width=w,joint="curve")

def arrow(d,x0,y0,x1,y1,color=BLUE,w=8):
    d.line([x0,y0,x1,y1],fill=color,width=w)
    ang=math.atan2(y1-y0,x1-x0); L=22
    for a in (ang-0.5,ang+0.5):
        d.line([x1,y1,x1-L*math.cos(a),y1-L*math.sin(a)],fill=color,width=w)

def stat(d,x,y,value,caption,vsize=150,color=WHITE,rule=BLUE,capw=520):
    d.rectangle([x,y+10,x+10,y+vsize*0.78],fill=rule)
    d.text((x+34,y-vsize*0.12),value,font=bebas(vsize),fill=color)
    yy=y+vsize*0.80
    body(d,yy,caption,size=28,color=MUTED,maxw=capw,x=x+34)

def pill(d,x,y,text,fg=BODY,bg=PILL,f=None,padx=26,pady=16):
    f=f or mb(24); w=tw(d,text,f)
    rrect(d,[x,y,x+w+2*padx,y+th(f)+2*pady],20,fill=bg)
    d.text((x+padx,y+pady-4),text,font=f,fill=fg)
    return x+w+2*padx

def card(d,box,fill=CARD,r=22,outline=LINE,width=2):
    rrect(d,box,r,fill=fill,outline=outline,width=width)

# ---------------- slides ----------------
def s01(d):
    y=eyebrow(d,300,"The only question that matters")
    y=title(d,y+10,"What does a breach cost?",size=170,accent={"COST?"})
    body(d,y+30,"Not a red / amber / green dot on a dashboard. A number — in pounds.",size=40,color=BODY)
    # RAG dots struck out, big £?
    cx=W-430; cy=380
    for i,c in enumerate([GREEN,AMBER,RED]):
        d.ellipse([cx+i*90,cy,cx+i*90+56,cy+56],fill=c)
    d.line([cx-14,cy+80,cx+280,cy-24],fill=WHITE,width=8)
    d.text((cx+70,cy+120),"£?",font=bebas(300),fill=BLUE)

def s02(d):
    y=eyebrow(d,300,"Governance today")
    y=title(d,y+10,"Compliance is theatre",size=170,accent={"THEATRE"})
    body(d,y+30,"A green tick that means nothing moved, nobody priced the risk,\nand nobody can say what changed when the world did.",size=38)
    # big COMPLIANT stamp with a crack
    bx,by,bw,bh=W-620,360,460,170
    rrect(d,[bx,by,bx+bw,by+bh],16,outline=GREEN,width=6)
    d.text((bx+40,by+34),"COMPLIANT",font=bebas(120),fill=GREEN)
    d.line([bx-20,by+bh+40,bx+bw+20,by-30],fill=RED,width=9)
    d.text((bx+120,by+bh+56),"a binary lie",font=mb(34),fill=RED)

def s03(d):
    y=eyebrow(d,280,"The idea")
    title(d,y+10,"Governance is a proportionate, informed, continuously re-tuned response to quantified risk",
          size=120,accent={"PROPORTIONATE,","QUANTIFIED","RISK"},lh=0.95)
    body(d,H-330,"Version the whole chain — appetite to evidence — and proportionality stays honest as the world moves.",size=36,color=MUTED)

def s04(d):
    y=eyebrow(d,300,"The reframe")
    y=title(d,y+10,"Policy is a versioned dependency",size=124,accent={"VERSIONED"},maxw=1060)
    body(d,y+26,"A lint pack your engineers already\nknow how to consume.",size=36,maxw=1000)
    bx,by,bw,bh=W-MARGIN-580,430,580,290
    card(d,[bx,by,bx+bw,by+bh])
    d.rectangle([bx,by,bx+bw,by+8],fill=BLUE)
    d.text((bx+40,by+40),"policy-pack",font=mb(38),fill=WHITE)
    d.text((bx+40,by+96),"v2.1.0",font=bebas(90),fill=BLUE)
    check(d,bx+bw-84,by+80,42); d.text((bx+bw-150,by+118),"signed",font=mb(24),fill=GREEN)
    px=bx+40
    for t in ["pin","sign","adopt by PR"]:
        px=pill(d,px,by+210,t,fg=BODY,f=mb(24))+16

def s05(d):
    eyebrow(d,190,"The mechanism")
    title(d,224,"The hourglass",size=120)
    cx=W//2; top=430; midy=690; bot=930
    halfw=560
    # top bulb (wide->neck)
    d.polygon([(cx-halfw,top),(cx+halfw,top),(cx+70,midy),(cx-70,midy)],fill=CARD,outline=LINE,width=2)
    # bottom bulb (neck->wide)
    d.polygon([(cx-70,midy),(cx+70,midy),(cx+halfw,bot),(cx-halfw,bot)],fill=CARD,outline=LINE,width=2)
    d.rectangle([cx-70,midy-6,cx+70,midy+6],fill=BLUE)
    # labels
    d.text((cx-tw(d,"RISK APPETITE  £",mb(34))/2,top+22),"RISK APPETITE  £",font=mb(34),fill=BLUE)
    for i,t in enumerate(["PRINCIPLES","CONTROLS  (Kyverno CEL)"]):
        d.text((cx-tw(d,t,mr(30))/2,top+90+i*46),t,font=mr(30),fill=BODY)
    d.text((cx-tw(d,"ENFORCEMENT",mb(30))/2,midy-42),"ENFORCEMENT",font=mb(30),fill=WHITE)
    d.text((cx-tw(d,"one admission decision",mr(24))/2,midy+16),"one admission decision",font=mr(24),fill=MUTED)
    for i,t in enumerate(["EVIDENCE  (OSCAL)","− EXEMPTIONS LEDGER"]):
        d.text((cx-tw(d,t,mr(30))/2,midy+70+i*46),t,font=mr(30),fill=BODY)
    d.text((cx-tw(d,"RESIDUAL RISK  £",mb(34))/2,bot-58),"RESIDUAL RISK  £",font=mb(34),fill=BLUE)
    # side arrows
    d.text((cx-halfw-150,top+60),"sets\ntone",font=mr(26),fill=MUTED)
    arrow(d,cx-halfw-40,top+70,cx-halfw+30,top+120,color=BLUE,w=6)
    arrow(d,cx+halfw+40,bot-40,cx+halfw+40,top+120,color=BLUE,w=6)
    d.text((cx+halfw+60,(top+bot)//2),"evidence\nflows up",font=mr(26),fill=MUTED)

def inst_card(d,x,y,w,h,tag,name,sub,color):
    card(d,[x,y,x+w,y+h]); d.rectangle([x,y,x+w,y+8],fill=color)
    d.text((x+34,y+34),tag,font=mb(26),fill=color)
    d.text((x+34,y+72),name,font=bebas(84),fill=WHITE)
    d.text((x+34,y+170),sub,font=mr(26),fill=MUTED)

def s06(d):
    y=eyebrow(d,250,"The money shot  ·  1 of 2")
    title(d,y+10,"Same control. Two institutions.",size=120,accent={"TWO"})
    inst_card(d,MARGIN,470,720,260,"RETAILER","driftwood","e-commerce · PCI + GDPR",AMBER)
    inst_card(d,W-MARGIN-720,470,720,260,"HOSPITAL","ludlow","US health · HIPAA",RED)
    # control chip in the middle
    cx=W//2
    rrect(d,[cx-190,540,cx+190,620],18,fill=BLUE)
    d.text((cx-tw(d,"encrypt at rest",mb(34))/2,558),"encrypt at rest",font=mb(34),fill=WHITE)
    d.text((cx-tw(d,"one identical rule",mr(24))/2,634),"one identical rule",font=mr(24),fill=MUTED)

def s07(d):
    y=eyebrow(d,230,"The money shot  ·  2 of 2")
    title(d,y+6,"Audit here. Deny there.",size=130,accent={"AUDIT"})
    # two verdict cards
    def verdict(x,tag,verd,color,who):
        card(d,[x,440,x+660,720]); d.rectangle([x,440,x+660,448],fill=color)
        d.text((x+40,470),who,font=mb(28),fill=MUTED)
        d.text((x+40,510),verd,font=bebas(150),fill=color)
        d.text((x+40,690-40),tag,font=mr(26),fill=BODY)
    verdict(MARGIN,"retail breach: lower £","AUDIT",AMBER,"driftwood")
    verdict(W-MARGIN-660,"health breach: ~8x £","DENY",RED,"ludlow")
    d.text((W//2-tw(d,"×8",bebas(120))/2,520),"×8",font=bebas(120),fill=BLUE)
    d.text((W//2-tw(d,"the £ decides",mb(28))/2,660),"the £ decides",font=mb(28),fill=WHITE)

def s08(d):
    y=eyebrow(d,250,"The number is real")
    title(d,y+10,"Priced, not guessed",size=140,accent={"PRICED,"})
    body(d,y+180,"Calibrated estimates → Monte Carlo → the tail your board fears.\nThe insurance industry's own maths.",size=34,color=BODY,maxw=760)
    # loss-exceedance curve
    gx,gy,gw,gh=W-820,430,660,380
    d.rectangle([gx,gy,gx+gw,gy+gh],outline=LINE,width=2)
    pts=[]
    for i in range(101):
        t=i/100; p=1-(t**0.55)   # exceedance prob descending
        pts.append((gx+t*gw, gy+ (1-p)*gh))
    d.line(pts,fill=BLUE,width=6,joint="curve")
    # area
    d.line([gx,gy+gh,gx+gw,gy+gh],fill=NEUT6,width=2)
    d.text((gx,gy-40),"loss-exceedance curve",font=mb(24),fill=MUTED)
    d.text((gx+gw-160,gy+gh+14),"£ loss →",font=mr(22),fill=MUTED)
    for i,(lbl,v) in enumerate([("ALE","mean"),("VaR₉₅","bad year"),("TVaR","the tail")]):
        px=gx+i*220
        d.text((px,gy+gh+56),lbl,font=mb(30),fill=BLUE)
        d.text((px,gy+gh+96),v,font=mr(22),fill=MUTED)

def s09(d):
    y=eyebrow(d,250,"And it moves")
    title(d,y+10,"Tighten a control — the £ falls",size=120,accent={"FALLS"})
    # before -> after
    stat(d,MARGIN,470,"£120k","residual risk · warn only",vsize=150,color=RED,rule=RED)
    arrow(d,MARGIN+560,540,MARGIN+760,540,color=BLUE,w=10)
    d.text((MARGIN+560,560),"tighten to Deny",font=mr(24),fill=MUTED)
    stat(d,MARGIN+820,470,"£18k","residual risk · enforced",vsize=150,color=GREEN,rule=GREEN)
    body(d,760,"Two runs. One input changed. The cost of a decision, live.",size=34,color=MUTED)

def s10(d):
    y=eyebrow(d,250,"No more exemptions")
    title(d,y+10,"You may X — if C",size=150,accent={"IF"})
    # strike EXEMPTION -> CONDITIONAL
    d.text((MARGIN,470),"EXEMPTION",font=bebas(90),fill=NEUT6)
    d.line([MARGIN-10,515,MARGIN+tw(d,"EXEMPTION",bebas(90)),515],fill=RED,width=8)
    arrow(d,MARGIN+560,505,MARGIN+700,505,color=BLUE,w=8)
    d.text((MARGIN+740,470),"CONDITIONAL POLICY",font=bebas(90),fill=BLUE)
    bx,by,bw,bh=MARGIN,600,W-2*MARGIN,150
    card(d,[bx,by,bx+bw,by+bh],fill=CARD2)
    d.text((bx+34,by+30),"allow  if  attestation ∧ data-class ≠ PII ∧ team ∈ {…} ∧ within-window",font=mono(30),fill=BODY)
    d.text((bx+34,by+84),"uniform · versioned · every branch carries its own priced residual £",font=mr(26),fill=MUTED)

def s11(d):
    y=eyebrow(d,250,"Failures move left")
    title(d,y+10,"Caught in CI, not at deploy",size=130,accent={"CI,"})
    bx,by,bw,bh=MARGIN,470,W-2*MARGIN,250
    card(d,[bx,by,bx+bw,by+bh])
    check(d,bx+70,by+120,54,color=GREEN,w=9)
    d.text((bx+150,by+40),"policy compatibility · ±1 version skew",font=mb(34),fill=WHITE)
    d.text((bx+150,by+92),"ran the target cluster's real admission action, offline",font=mr(28),fill=BODY)
    d.text((bx+150,by+140),"Audit → Deny flip caught before merge",font=mr(28),fill=AMBER)
    pill(d,bx+bw-260,by+96,"CI  ·  passed",fg=GREEN,bg=(18,40,30))
    body(d,760,"A deploy-time surprise becomes practically unheard of.",size=34,color=MUTED)

def feedpill(d,x,y,t):
    return pill(d,x,y,t,fg=BODY,bg=PILL,f=mb(26))
def s12(d):
    y=eyebrow(d,250,"The living loop")
    title(d,y+10,"The estate war-games itself",size=130,accent={"WAR-GAMES"})
    x=MARGIN; yy=480
    for t in ["threat feeds","CVE","end-of-life","penalties","market-intel"]:
        x=feedpill(d,x,yy,t)+18
    # arrow to war-gamer node
    arrow(d,MARGIN+300,yy+120,MARGIN+300,yy+170,color=BLUE,w=8)
    bx,by,bw,bh=MARGIN,yy+190,760,180
    card(d,[bx,by,bx+bw,by+bh]); d.rectangle([bx,by,bx+8,by+bh],fill=BLUE)
    d.text((bx+34,by+34),"WAR-GAMER",font=bebas(70),fill=WHITE)
    d.text((bx+34,by+118),"stress-tests controls · is this still proportionate?",font=mr(26),fill=MUTED)
    arrow(d,bx+bw+40,by+90,bx+bw+180,by+90,color=BLUE,w=8)
    d.text((bx+bw+210,by+40),"drift?",font=mb(40),fill=BLUE)
    d.text((bx+bw+210,by+100),"the world moved.",font=mr(26),fill=MUTED)

def s13(d):
    y=eyebrow(d,240,"Propose, never dispose")
    title(d,y+6,"The AI opens a PR",size=140,accent={"PR"})
    bx,by,bw,bh=MARGIN,440,W-2*MARGIN,300
    card(d,[bx,by,bx+bw,by+bh])
    d.rectangle([bx,by,bx+8,by+bh],fill=GREEN)
    d.text((bx+40,by+30),"Retune encrypt-at-rest → Deny in ludlow",font=mb(36),fill=WHITE)
    d.text((bx+40,by+86),"war-gamer[bot]  wants to merge into  main",font=mr(28),fill=MUTED)
    px=bx+40
    px=pill(d,px,by+140,"open",fg=GREEN,bg=(18,40,30))+16
    px=pill(d,px,by+140,"gitsign · signed",fg=BLUE,bg=(16,30,60))+16
    px=pill(d,px,by+140,"pr-gate · version check",fg=BLUE,bg=(16,30,60))+16
    pill(d,bx+40,by+215,"awaiting human review",fg=AMBER,bg=(45,35,15))
    d.text((bx+bw-390,by+222),"proposes — never merges",font=mb(28),fill=RED)

def s14(d):
    y=eyebrow(d,250,"Verify, don't trust")
    title(d,y+10,"Every actor signs",size=150,accent={"SIGNS"})
    bx,by,bw,bh=MARGIN,470,W-2*MARGIN,240
    card(d,[bx,by,bx+bw,by+bh],fill=CARD2)
    check(d,bx+70,by+120,54,color=GREEN,w=9)
    d.text((bx+150,by+40),"gitsign (keyless)  →  Rekor transparency log",font=mb(34),fill=WHITE)
    d.text((bx+150,by+96),"actor: war-gamer[bot]   from: cve-feed@v2026.07   verdict: signed",font=mono(26),fill=BODY)
    d.text((bx+150,by+146),"which actor proposed what, when, from which evidence — provable",font=mr(26),fill=MUTED)
    pill(d,bx+bw-240,by+96,"VERIFIED",fg=GREEN,bg=(18,40,30))

def orgnode(d,x,y,w,h,name,sub,color=CARD,edge=LINE,tcol=WHITE):
    card(d,[x,y,x+w,y+h],fill=color,outline=edge,width=2)
    d.text((x+24,y+22),name,font=mb(30),fill=tcol)
    d.text((x+24,y+62),sub,font=mr(22),fill=MUTED)

def s15(d):
    eyebrow(d,170,"None of this is slideware")
    title(d,204,"Six real orgs. All live.",size=110,accent={"SIX"})
    # regulators
    orgnode(d,MARGIN,420,330,110,"…-nist","OSCAL controls (real)")
    orgnode(d,MARGIN,560,330,110,"…-ico","penalties → £ (real)")
    # platform
    px,py,pw,ph=680,440,520,210
    card(d,[px,py,px+pw,py+ph],fill=CARD,outline=BLUE,width=3)
    d.rectangle([px,py,px+pw,py+8],fill=BLUE)
    d.text((px+28,py+30),"…-platform",font=mb(38),fill=WHITE)
    d.text((px+28,py+82),"the shared discipline",font=mr(26),fill=BLUE)
    d.text((px+28,py+124),"FAIR engine · war-gamer · Flux\nledger render · shift-left · OSCAL",font=mr(23),fill=MUTED)
    # institutions
    for i,(n,s2,c) in enumerate([("…-driftwood","retail · LIVE",AMBER),
                                 ("…-tuppence","fintech · LIVE",BLUE),
                                 ("…-ludlow","health · LIVE",RED)]):
        orgnode(d,1360,420+i*150,400,120,n,s2,edge=c,tcol=WHITE)
    arrow(d,MARGIN+330,475,660,520,color=BLUE,w=5)
    arrow(d,MARGIN+330,615,660,590,color=BLUE,w=5)
    for i in range(3):
        arrow(d,px+pw+20,545,1340,480+i*150,color=BLUE,w=5)
    d.text((px+pw+40,545+120),"pinned, signed",font=mr(22),fill=MUTED)

def s16(d):
    y=eyebrow(d,250,"The close")
    title(d,y+10,"Risk on the balance sheet",size=130,accent={"BALANCE"})
    body(d,y+180,"Residual risk becomes economic capital. An underwriter would\nprice the very same controls we enforce.",size=36,maxw=820)
    stat(d,W-720,470,"a line","your board can read, defend and act on",vsize=140,color=WHITE,rule=BLUE,capw=560)
    pill(d,W-720,700,"insurable",fg=BLUE,bg=(16,30,60))
    pill(d,W-540,700,"board-legible",fg=BLUE,bg=(16,30,60))

def s17(d):
    y=eyebrow(d,250,"Why this is ours to build")
    title(d,y+10,"Flux is load-bearing",size=150,accent={"LOAD-BEARING"})
    body(d,y+180,"Not a logo on a slide — the spine. Six real jobs:",size=36)
    jobs=["distribution","provenance","prune-on-retire","drift-heal","ordering","events"]
    x=MARGIN; yy=560
    for i,j in enumerate(jobs):
        if i==3: x=MARGIN; yy+=110
        x=pill(d,x,yy,j,fg=WHITE,bg=BLUE_DK,f=mb(30))+22

def s18(d):
    y=eyebrow(d,250,"The payoff")
    title(d,y+10,"What you get",size=150)
    items=[("FLAGSHIP TALK","a conference talk that tours"),
           ("DEMO ESTATE","reusable in front of any prospect"),
           ("THE NARRATIVE","own a story no competitor tells")]
    cw=(W-2*MARGIN-2*40)//3
    for i,(t,s2) in enumerate(items):
        x=MARGIN+i*(cw+40); card(d,[x,470,x+cw,760])
        d.rectangle([x,470,x+cw,478],fill=BLUE)
        d.text((x+30,510),f"0{i+1}",font=bebas(90),fill=BLUE)
        d.text((x+30,620),t,font=mb(34),fill=WHITE)
        body(d,668,s2,size=26,color=MUTED,maxw=cw-60,x=x+30)

def s19(d):
    y=eyebrow(d,240,"The commitment")
    title(d,y+6,"Nothing is a nice-to-have",size=130,accent={"NOTHING"})
    items=["FAIR risk engine","conditional policy","the living loop","provenance for every actor","OSCAL up-flow","balance sheet","six live orgs","the flagship talk"]
    x0=MARGIN; y0=470; cw=(W-2*MARGIN)//2
    for i,t in enumerate(items):
        col=i%2; row=i//2
        x=x0+col*cw; yy=y0+row*100
        check(d,x+24,yy+22,34,color=BLUE,w=7)
        d.text((x+80,yy),t,font=mb(38),fill=WHITE)
    body(d,H-210,"Built fresh. All real. All versioned. Nothing faked, nothing hinted.",size=32,color=MUTED)

def s20(d):
    # CTA panel
    card(d,[MARGIN,250,W-MARGIN,H-140],fill=CARD,outline=BLUE,width=3)
    eyebrow(d,360,"The ask")
    title(d,400,"Fund it.",size=260,accent={"IT."})
    body(d,700,"End to end — through to the flagship talk. I'll hand you the estate that proves\ngovernance can finally be proportionate, honest, and alive.",size=38,maxw=W-2*MARGIN-120)
    bx,by=MARGIN+70,850
    rrect(d,[bx,by,bx+520,by+92],14,fill=BLUE)
    d.text((bx+44,by+24),"FUND THE BUILD",font=mb(40),fill=WHITE)
    d.text((bx+600,by+26),"risk on the balance sheet.",font=mr(32),fill=MUTED)

SLIDES=[s01,s02,s03,s04,s05,s06,s07,s08,s09,s10,s11,s12,s13,s14,s15,s16,s17,s18,s19,s20]

if __name__=="__main__":
    for i,fn in enumerate(SLIDES,1):
        img,d=base(i); fn(d)
        img.save(OUT/f"s{i:02d}.png")
        print(f"rendered s{i:02d}")
    print("done")
