import os, json, math, time, random
from datetime import datetime, timedelta
import streamlit as st

st.set_page_config(
    page_title="AEGIS — AI Decision & Planning Engine",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--bg:#07090d;--card:#10131a;--line:rgba(255,255,255,.08);--muted:#7d8595;--text:#f4f5fa;--accent:#8c70ff;--accent2:#5e45d8;--good:#5ce39a}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 12% 8%,rgba(111,76,255,.14),transparent 27%),radial-gradient(circle at 90% 85%,rgba(39,116,255,.10),transparent 28%),#07090d;color:var(--text)}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.10;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:55px 55px;mask-image:radial-gradient(circle at 50%,black,transparent 80%)}
.block-container{max-width:1240px;padding-top:2rem;padding-bottom:4rem}
h1,h2,h3,h4{font-family:"Space Grotesk",sans-serif}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:18px}
.logo-mark{width:40px;height:40px;border:1px solid rgba(140,112,255,.45);border-radius:12px;display:grid;place-items:center;color:#b3a5ff;background:rgba(140,112,255,.08);box-shadow:0 0 30px rgba(140,112,255,.16);font-size:21px}
.logo-name{font:700 19px "Space Grotesk";letter-spacing:.18em}
.logo-sub{font-size:7px;letter-spacing:.15em;color:#697180;margin-top:2px}
.glass{background:linear-gradient(145deg,rgba(20,23,31,.92),rgba(11,13,18,.86));border:1px solid var(--line);border-radius:18px;box-shadow:0 24px 70px rgba(0,0,0,.35),inset 0 1px rgba(255,255,255,.025);padding:24px}
.eyebrow{font-size:9px;font-weight:700;letter-spacing:.16em;color:#9aa1af;text-transform:uppercase}
.pulse{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 14px var(--good);margin-right:7px}
.hero-title{font:600 clamp(42px,6vw,74px) "Space Grotesk";letter-spacing:-.055em;line-height:.98;margin:18px 0}
.hero-title span{color:#9b87ff}
.muted{color:var(--muted);line-height:1.75;font-size:12px}
.orb{width:150px;height:150px;border-radius:50%;margin:auto;position:relative;display:grid;place-items:center}
.orb:before,.orb:after{content:"";position:absolute;border:1px solid rgba(157,137,255,.35);border-radius:50%;inset:4%;transform:scaleY(.36) rotate(22deg);box-shadow:0 0 30px rgba(124,92,255,.08)}
.orb:after{inset:13%;transform:scaleY(.55) rotate(-38deg);border-color:rgba(89,194,255,.20)}
.core{width:53px;height:53px;border-radius:50%;background:radial-gradient(circle at 32% 27%,#fff,#9b87ff 28%,#4a31bd 62%,#120c28);box-shadow:0 0 45px rgba(132,103,255,.8),0 0 110px rgba(124,92,255,.18)}
.stButton>button{border-radius:11px!important;border:1px solid var(--line)!important;background:rgba(255,255,255,.035)!important;color:#d9dce4!important;min-height:44px;font-weight:600}
.stButton>button:hover{border-color:rgba(140,112,255,.65)!important;background:rgba(140,112,255,.10)!important}
.primary-btn .stButton>button{background:linear-gradient(135deg,#8a6cff,#6042dc)!important;border:0!important;color:white!important;box-shadow:0 10px 30px rgba(94,65,230,.25)}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stNumberInput"] input{background:#090b10!important;border:1px solid var(--line)!important;color:#eee!important;border-radius:10px!important}
label{color:#aeb4c0!important;font-size:11px!important}
.metric{padding:18px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.025)}
.metric b{font:600 27px "Space Grotesk";display:block}
.metric small{color:#707887;font-size:9px;letter-spacing:.08em}
.tag{display:inline-block;padding:7px 10px;border:1px solid rgba(140,112,255,.22);border-radius:999px;color:#b7aaff;background:rgba(140,112,255,.07);font-size:9px;margin:3px}
.timeline{border-left:1px solid rgba(140,112,255,.35);padding-left:22px;margin-left:10px}
.titem{position:relative;margin:0 0 22px}
.titem:before{content:"";position:absolute;left:-28px;top:4px;width:9px;height:9px;border-radius:50%;background:#8065ff;box-shadow:0 0 12px #8065ff}
.titem b{font-size:11px}.titem small{display:block;color:#707887;margin-top:4px;font-size:9px}
.reason{padding:15px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.025);margin:8px 0}
.reason b{font-size:10px}.reason p{font-size:9px;color:#7d8594;margin:6px 0 0;line-height:1.6}
.progress-wrap{height:5px;background:rgba(255,255,255,.06);border-radius:9px;overflow:hidden}.progress-bar{height:100%;background:linear-gradient(90deg,#6347df,#aa99ff);box-shadow:0 0 15px #8065ff}
hr{border-color:var(--line)}
.smallcaps{font-size:9px;letter-spacing:.14em;color:#727a89;text-transform:uppercase}
div[data-testid="stSidebar"]{background:#090b10;border-right:1px solid var(--line)}
@media(max-width:800px){.hero-title{font-size:45px}.glass{padding:18px}.orb{margin:25px auto}}
</style>
""", unsafe_allow_html=True)

# ---------------- STATE ----------------
if "screen" not in st.session_state: st.session_state.screen="launch"
if "email" not in st.session_state: st.session_state.email=""
if "plan" not in st.session_state: st.session_state.plan=None
if "priority" not in st.session_state: st.session_state.priority="Balanced"
if "type" not in st.session_state: st.session_state.type="Travel"

def logo():
    st.markdown('<div class="brand"><div class="logo-mark">◈</div><div><div class="logo-name">AEGIS</div><div class="logo-sub">AI DECISION & PLANNING ENGINE</div></div></div>',unsafe_allow_html=True)

def orb():
    st.markdown('<div class="orb"><div class="core"></div></div>',unsafe_allow_html=True)

def go(screen):
    st.session_state.screen=screen
    st.rerun()

# ---------------- LAUNCH ----------------
if st.session_state.screen=="launch":
    logo()
    st.write("")
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        orb()
        st.markdown('<div style="text-align:center"><div class="hero-title" style="font-size:48px">AEGIS</div><div class="eyebrow">AI DECISION & PLANNING ENGINE</div><br><span class="pulse"></span><span class="eyebrow">AI CORE ONLINE</span></div>',unsafe_allow_html=True)
        st.progress(100,text="Initializing intelligence core")
        st.markdown('<div style="text-align:center;color:#555d6b;font-size:8px;letter-spacing:.12em">SECURE SESSION · BUILD 01.26 · LOCAL CORE</div>',unsafe_allow_html=True)
        time.sleep(.35)
        go("login")

# ---------------- LOGIN ----------------
elif st.session_state.screen=="login":
    logo()
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.markdown('<div class="eyebrow"><span class="pulse"></span>INTELLIGENCE SYSTEM ONLINE</div>',unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Think less.<br><span>Plan smarter.</span></div>',unsafe_allow_html=True)
        st.markdown('<p class="muted" style="max-width:570px">AEGIS researches, compares and optimizes your plans — then explains every important decision.</p>',unsafe_allow_html=True)
        st.write("")
        st.markdown('<span class="tag">✦ Autonomous planning</span><span class="tag">⚡ Real-time optimization</span><span class="tag">◎ Decision intelligence</span>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass">',unsafe_allow_html=True)
        st.markdown('<div class="smallcaps">SECURE ACCESS</div><h2 style="margin-top:8px">Welcome back</h2><p class="muted">Enter your credentials to continue.</p>',unsafe_allow_html=True)
        email=st.text_input("Email address",placeholder="you@example.com",value=st.session_state.email)
        pw=st.text_input("Password",type="password",placeholder="••••••••")
        if st.button("Sign in  →",use_container_width=True,disabled=not(email and pw)):
            st.session_state.email=email
            go("setup")
        st.write("")
        st.button("◉  Continue with biometric",use_container_width=True)
        st.markdown('<p style="text-align:center;color:#626977;font-size:10px">New to AEGIS? <span style="color:#a08cff">Create an account</span></p>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

# ---------------- SETUP ----------------
elif st.session_state.screen=="setup":
    logo()
    st.markdown('<div class="eyebrow">✦ PERSONALIZE AEGIS</div><div class="hero-title" style="font-size:50px">Let’s tune your<br><span>intelligence.</span></div><p class="muted">Two quick choices. AEGIS will use them to shape better recommendations.</p>',unsafe_allow_html=True)
    st.markdown("### 01  What do you usually plan?")
    opts=["Travel","Business","Study","Anything"]
    cols=st.columns(4)
    for i,x in enumerate(opts):
        with cols[i]:
            if st.button(("✓  " if st.session_state.type==x else "")+x,use_container_width=True,key="type_"+x):
                st.session_state.type=x;st.rerun()
    st.markdown("### 02  What matters most?")
    cols=st.columns(4)
    for i,x in enumerate(["Save time","Save money","Best experience","Balanced"]):
        with cols[i]:
            if st.button(("✓  " if st.session_state.priority==x else "")+x,use_container_width=True,key="pri_"+x):
                st.session_state.priority=x;st.rerun()
    st.divider()
    if st.button("Continue  →",use_container_width=True):
        go("intro")

# ---------------- INTRO ----------------
elif st.session_state.screen=="intro":
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        orb()
        st.markdown('<div style="text-align:center"><div class="eyebrow">✦ YOUR AI PLANNING ENGINE</div><div class="hero-title" style="font-size:48px">Tell me what you need.<br><span>I’ll figure out the rest.</span></div><p class="muted">I can research options, compare alternatives, optimize schedules and explain the decisions that shape your plan.</p><span class="tag">◎ Research</span><span class="tag">◇ Compare</span><span class="tag">⚡ Optimize</span><span class="tag">✦ Decide</span></div>',unsafe_allow_html=True)
        st.write("")
        st.info('Example: “Plan a weekend trip under Rs. 50,000…”')
        if st.button("Enter AEGIS  →",use_container_width=True):
            go("dashboard")

# ---------------- DASHBOARD ----------------
elif st.session_state.screen=="dashboard":
    with st.sidebar:
        logo()
        st.markdown("### AEGIS")
        if st.button("⌂  Home",use_container_width=True): go("dashboard")
        if st.button("＋  New plan",use_container_width=True): go("create")
        if st.button("◈  Insights",use_container_width=True): go("insights")
        st.divider()
        st.caption("CORE STATUS")
        st.success("AI Core Online")
    logo()
    st.markdown('<div class="eyebrow"><span class="pulse"></span>AI CORE READY</div><div class="hero-title" style="font-size:50px">Good evening.<br><span>What do you want to plan?</span></div><p class="muted">Describe an objective in plain language. AEGIS will research the options, resolve constraints and build the best plan.</p>',unsafe_allow_html=True)
    prompt=st.text_input("Command",placeholder="e.g. Plan a 2-day Karachi trip for 2 people under Rs. 50,000...",label_visibility="collapsed")
    if st.button("✦  Create plan",use_container_width=True):
        st.session_state.prompt=prompt or "Plan a 2-day Karachi trip for 2 people under Rs. 50,000"
        go("create")
    st.write("")
    left,right=st.columns([1.5,.8],gap="large")
    with left:
        st.markdown('<div class="glass"><div class="smallcaps">YOUR WORKSPACE</div><h2>Recent plans</h2>',unsafe_allow_html=True)
        for name,sub,score,budget in [("Karachi Weekend","Travel · 2 days","91%","Rs. 43,750"),("Client Strategy Day","Business · 1 day","87%","Rs. 12,400"),("Final Exam Week","Study · 7 days","94%","32 hrs")]:
            a,b,c,d=st.columns([1.7,1,.6,.7])
            with a: st.markdown(f"**{name}**<br><span style='color:#666f7d;font-size:9px'>{sub}</span>",unsafe_allow_html=True)
            with b: st.markdown(f"<span style='color:#aaa5d0;font-size:9px'>{budget}</span>",unsafe_allow_html=True)
            with c: st.markdown(f"<span style='color:#68e3a0;font-size:10px'>{score}</span>",unsafe_allow_html=True)
            with d: st.button("›",key=name)
            st.divider()
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass"><div class="smallcaps">AEGIS INSIGHT</div><h2>Your planning efficiency is up.</h2><p class="muted">AEGIS has optimized <b>12 decisions</b> across your recent plans.</p><div class="metric"><small>EFFICIENCY</small><b>+24%</b></div></div>',unsafe_allow_html=True)

# ---------------- CREATE ----------------
elif st.session_state.screen=="create":
    logo()
    st.markdown('<div class="eyebrow">✦ NEW PLAN</div><div class="hero-title" style="font-size:48px">Give AEGIS an objective.</div>',unsafe_allow_html=True)
    default=getattr(st.session_state,"prompt","Plan a 2-day Karachi trip for 2 people under Rs. 50,000")
    prompt=st.text_area("Objective",value=default,height=100)
    c1,c2,c3,c4=st.columns(4)
    with c1: city=st.text_input("Location","Karachi")
    with c2: days=st.number_input("Duration (days)",1,14,2)
    with c3: people=st.number_input("People",1,20,2)
    with c4: budget=st.number_input("Budget (Rs.)",1000,1000000,50000,step=1000)
    st.markdown("### AEGIS constraints")
    st.markdown(f'<span class="tag">LOCATION · {city}</span><span class="tag">DURATION · {days} DAYS</span><span class="tag">PEOPLE · {people}</span><span class="tag">BUDGET · Rs. {budget:,}</span><span class="tag">PRIORITY · {st.session_state.priority}</span>',unsafe_allow_html=True)
    if st.button("✦  Run AEGIS",use_container_width=True):
        st.session_state.plan={"city":city,"days":days,"people":people,"budget":budget,"prompt":prompt}
        go("processing")

# ---------------- PROCESSING ----------------
elif st.session_state.screen=="processing":
    logo()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        orb()
        st.markdown('<div style="text-align:center"><div class="eyebrow">AEGIS IS THINKING</div><h2>Building your optimal plan</h2></div>',unsafe_allow_html=True)
        steps=["Understanding request","Analyzing constraints","Researching options","Comparing alternatives","Optimizing plan","Preparing recommendation"]
        box=st.empty()
        bar=st.progress(0)
        for i,s in enumerate(steps):
            time.sleep(.20)
            box.markdown("  \n".join([("✓" if j<=i else "○")+"  "+x for j,x in enumerate(steps)]))
            bar.progress(int((i+1)/len(steps)*100))
        go("workspace")

# ---------------- WORKSPACE ----------------
elif st.session_state.screen=="workspace":
    p=st.session_state.plan or {"city":"Karachi","days":2,"people":2,"budget":50000}
    logo()
    st.markdown(f'<div class="eyebrow"><span class="pulse"></span>OPTIMIZED BY AEGIS</div><div class="hero-title" style="font-size:46px">{p["city"]} Weekend</div>',unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    for col,title,val in zip([a,b,c,d],["OPTIMIZATION SCORE","TOTAL BUDGET","DURATION","PEOPLE"],["91 / 100",f'Rs. {int(p["budget"]*.875):,}',f'{p["days"]} days',str(p["people"])]):
        with col: st.markdown(f'<div class="metric"><small>{title}</small><b>{val}</b></div>',unsafe_allow_html=True)
    st.write("")
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.markdown('<div class="glass"><div class="smallcaps">SCHEDULE</div><h2>Optimized timeline</h2><div class="timeline">',unsafe_allow_html=True)
        items=[("09:00","Breakfast & city start"),("10:30","Heritage / cultural activity"),("13:00","Lunch"),("15:00","Curated afternoon activity"),("18:30","Sunset & leisure"),("20:00","Dinner")]
        for t,x in items: st.markdown(f'<div class="titem"><b>{t} — {x}</b><small>AEGIS selected this slot to minimize unnecessary travel.</small></div>',unsafe_allow_html=True)
        st.markdown('</div></div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="glass"><div class="smallcaps">BUDGET</div><h2>Rs. 43,750</h2>',unsafe_allow_html=True)
        for x,v in [("Accommodation",16000),("Transport",8500),("Food",10500),("Activities",8750)]:
            pct=v/43750*100
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:10px"><span>{x}</span><span>Rs. {v:,}</span></div><div class="progress-wrap" style="margin:6px 0 13px"><div class="progress-bar" style="width:{pct}%"></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">AI DECISIONS</div><h2>Why AEGIS chose this plan</h2>',unsafe_allow_html=True)
    for title,txt in [("Hotel selected","Best balance between location, price and the selected priority."),("Route optimized","Reduced unnecessary travel between activities and meal stops."),("Budget protected","The plan keeps a safety margin instead of spending the full limit."),("Schedule balanced","High-value activities are spaced to avoid an exhausting day.")]:
        st.markdown(f'<div class="reason"><b>{title}</b><p>{txt}</p></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    c1,c2=st.columns(2)
    with c1:
        if st.button("↻  What If? Optimize",use_container_width=True): go("whatif")
    with c2:
        if st.button("←  Back to Command Center",use_container_width=True): go("dashboard")

# ---------------- WHAT IF ----------------
elif st.session_state.screen=="whatif":
    p=st.session_state.plan or {"city":"Karachi","days":2,"people":2,"budget":50000}
    logo()
    st.markdown('<div class="eyebrow">◈ SCENARIO SIMULATOR</div><div class="hero-title" style="font-size:48px">What if we change the rules?</div><p class="muted">Adjust a constraint and let AEGIS re-optimize the plan.</p>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: nb=st.number_input("Budget (Rs.)",10000,1000000,int(p["budget"]),step=5000)
    with c2: np=st.number_input("People",1,20,int(p["people"]))
    with c3: nd=st.number_input("Duration",1,14,int(p["days"]))
    priority=st.selectbox("New priority",["Balanced","Save time","Save money","Best experience"],index=["Balanced","Save time","Save money","Best experience"].index(st.session_state.priority) if st.session_state.priority in ["Balanced","Save time","Save money","Best experience"] else 0)
    st.write("")
    old_score=91
    delta=0
    if nb<p["budget"]: delta-=6
    if nb>p["budget"]: delta+=2
    if np>p["people"]: delta-=3
    if nd>p["days"]: delta-=1
    if priority=="Save money": delta+=1
    new=max(55,min(98,old_score+delta))
    a,b=st.columns(2)
    with a: st.markdown(f'<div class="metric"><small>BEFORE</small><b>{old_score} / 100</b><span style="color:#707887;font-size:9px">Current optimized plan</span></div>',unsafe_allow_html=True)
    with b: st.markdown(f'<div class="metric"><small>AFTER</small><b>{new} / 100</b><span style="color:#68e3a0;font-size:9px">AI scenario estimate</span></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">EXPECTED CHANGES</div><h2>AEGIS would adapt</h2>',unsafe_allow_html=True)
    changes=[]
    if nb!=p["budget"]: changes.append("Budget allocation and accommodation tier")
    if np!=p["people"]: changes.append("Transport and room configuration")
    if nd!=p["days"]: changes.append("Activity density and schedule")
    if priority!=st.session_state.priority: changes.append("Recommendations weighted toward the new priority")
    if not changes: changes=["No major changes — current plan already matches these constraints."]
    for x in changes: st.markdown(f'<div class="reason"><b>↻ {x}</b><p>AEGIS would recalculate connected decisions instead of simply changing one field.</p></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.write("")
    if st.button("✦  Apply Scenario",use_container_width=True):
        st.session_state.plan.update({"budget":nb,"people":np,"days":nd})
        st.session_state.priority=priority
        go("workspace")

# ---------------- INSIGHTS ----------------
elif st.session_state.screen=="insights":
    logo()
    st.markdown('<div class="eyebrow">✦ AEGIS INSIGHTS</div><div class="hero-title" style="font-size:50px">Your decisions,<br><span>made measurable.</span></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    for col,title,val,sub in [(a,"PLANS OPTIMIZED","12","+24% efficiency"),(b,"DECISIONS","47","Across recent plans"),(c,"AVG. SCORE","91","Optimization quality")]:
        with col: st.markdown(f'<div class="metric"><small>{title}</small><b>{val}</b><span style="color:#68e3a0;font-size:9px">{sub}</span></div>',unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">HOW AEGIS HELPS</div><h2>From request → reasoning → outcome</h2>',unsafe_allow_html=True)
    for i,(x,y) in enumerate([("01","Understand","Natural language becomes structured constraints."),("02","Research","Relevant alternatives are identified and compared."),("03","Optimize","Trade-offs are evaluated against your priorities."),("04","Explain","The final recommendation comes with reasons.")]):
        st.markdown(f'<div class="reason"><b>{x} · {y}</b><p>{y}</p><p>{y if False else ""}</p></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    if st.button("← Back to Command Center",use_container_width=True): go("dashboard")
