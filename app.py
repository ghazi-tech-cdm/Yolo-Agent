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
:root{--bg:#05070b;--card:#0d1118;--card2:#111722;--line:rgba(255,255,255,.08);--muted:#7e8798;--text:#f4f5fa;--accent:#8b72ff;--accent2:#5e45d8;--good:#55e59a}
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 10% 0%,rgba(105,75,255,.16),transparent 27%),radial-gradient(circle at 95% 90%,rgba(38,121,255,.09),transparent 30%),#05070b;color:var(--text)}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.10;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:55px 55px;mask-image:radial-gradient(circle at 50%,black,transparent 80%)}
.block-container{max-width:1260px;padding-top:1.7rem;padding-bottom:4rem}
h1,h2,h3,h4{font-family:"Space Grotesk",sans-serif}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:22px}.logo-mark{width:40px;height:40px;border:1px solid rgba(140,112,255,.45);border-radius:12px;display:grid;place-items:center;color:#b3a5ff;background:rgba(140,112,255,.08);box-shadow:0 0 30px rgba(140,112,255,.16);font-size:21px}.logo-name{font:700 19px "Space Grotesk";letter-spacing:.18em}.logo-sub{font-size:7px;letter-spacing:.15em;color:#697180;margin-top:2px}
.glass{background:linear-gradient(145deg,rgba(19,23,32,.96),rgba(9,12,17,.92));border:1px solid var(--line);border-radius:18px;box-shadow:0 24px 70px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.025);padding:23px}
.eyebrow{font-size:9px;font-weight:700;letter-spacing:.16em;color:#9aa1af;text-transform:uppercase}.pulse{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 14px var(--good);margin-right:7px}
.hero-title{font:600 clamp(42px,6vw,72px) "Space Grotesk";letter-spacing:-.055em;line-height:.98;margin:18px 0}.hero-title span{color:#9b87ff}.muted{color:var(--muted);line-height:1.7;font-size:12px}
.orb{width:150px;height:150px;border-radius:50%;margin:auto;position:relative;display:grid;place-items:center}.orb:before,.orb:after{content:"";position:absolute;border:1px solid rgba(157,137,255,.35);border-radius:50%;inset:4%;transform:scaleY(.36) rotate(22deg);box-shadow:0 0 30px rgba(124,92,255,.08)}.orb:after{inset:13%;transform:scaleY(.55) rotate(-38deg);border-color:rgba(89,194,255,.20)}.core{width:53px;height:53px;border-radius:50%;background:radial-gradient(circle at 32% 27%,#fff,#9b87ff 28%,#4a31bd 62%,#120c28);box-shadow:0 0 45px rgba(132,103,255,.8),0 0 110px rgba(124,92,255,.18)}
.stButton>button{border-radius:11px!important;border:1px solid var(--line)!important;background:rgba(255,255,255,.035)!important;color:#d9dce4!important;min-height:44px;font-weight:600}.stButton>button:hover{border-color:rgba(140,112,255,.65)!important;background:rgba(140,112,255,.10)!important}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea,div[data-testid="stNumberInput"] input{background:#090b10!important;border:1px solid var(--line)!important;color:#eee!important;border-radius:10px!important}label{color:#aeb4c0!important;font-size:11px!important}
.metric{padding:18px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.025)}.metric b{font:600 26px "Space Grotesk";display:block}.metric small{color:#707887;font-size:9px;letter-spacing:.08em}
.tag{display:inline-block;padding:7px 10px;border:1px solid rgba(140,112,255,.22);border-radius:999px;color:#b7aaff;background:rgba(140,112,255,.07);font-size:9px;margin:3px}
.module{min-height:160px;cursor:pointer}.module-icon{font-size:25px;color:#aa9bff;margin-bottom:20px}.module-title{font:600 17px "Space Grotesk"}.module-sub{font-size:10px;color:#737c8c;line-height:1.55;margin-top:7px}.module-arrow{float:right;color:#686f7c}
.timeline{border-left:1px solid rgba(140,112,255,.35);padding-left:22px;margin-left:10px}.titem{position:relative;margin:0 0 22px}.titem:before{content:"";position:absolute;left:-28px;top:4px;width:9px;height:9px;border-radius:50%;background:#8065ff;box-shadow:0 0 12px #8065ff}.titem b{font-size:11px}.titem small{display:block;color:#707887;margin-top:4px;font-size:9px}
.reason{padding:15px;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.025);margin:8px 0}.reason b{font-size:10px}.reason p{font-size:9px;color:#7d8594;margin:6px 0 0;line-height:1.6}
.progress-wrap{height:5px;background:rgba(255,255,255,.06);border-radius:9px;overflow:hidden}.progress-bar{height:100%;background:linear-gradient(90deg,#6347df,#aa99ff);box-shadow:0 0 15px #8065ff}
.ticket{position:relative;background:linear-gradient(135deg,#f4f2ff,#d9d5ff);color:#12131a;border-radius:18px;padding:22px;overflow:hidden}.ticket:after{content:"";position:absolute;right:-55px;top:-55px;width:150px;height:150px;border-radius:50%;border:30px solid rgba(100,73,220,.10)}.ticket-top{display:flex;justify-content:space-between;align-items:center}.ticket-brand{font:700 12px "Space Grotesk";letter-spacing:.12em}.ticket-code{font:700 10px;letter-spacing:.12em;color:#5e6070}.airport{font:700 28px "Space Grotesk";letter-spacing:-.04em}.flightline{height:1px;background:rgba(20,20,30,.18);margin:16px 0}.ticket-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}.ticket-label{font-size:7px;color:#6e7080;text-transform:uppercase;letter-spacing:.12em}.ticket-value{font-size:10px;font-weight:700;margin-top:3px}.barcode{height:34px;margin-top:18px;background:repeating-linear-gradient(90deg,#111 0 2px,transparent 2px 5px,#111 5px 6px,transparent 6px 9px);opacity:.85}
.hotel-card{border:1px solid var(--line);border-radius:15px;overflow:hidden;background:rgba(255,255,255,.025)}.hotel-visual{height:115px;background:radial-gradient(circle at 75% 30%,rgba(140,112,255,.55),transparent 25%),linear-gradient(135deg,#202333,#0e1118);display:flex;align-items:end;padding:14px}.hotel-visual span{font-size:8px;letter-spacing:.12em;color:#ddd}
.stTabs [data-baseweb="tab-list"]{gap:5px;background:transparent}.stTabs [data-baseweb="tab"]{background:rgba(255,255,255,.025);border:1px solid var(--line);border-radius:9px;padding:8px 14px;font-size:10px}.stTabs [aria-selected="true"]{background:rgba(139,114,255,.14);border-color:rgba(139,114,255,.45)}
.smallcaps{font-size:9px;letter-spacing:.14em;color:#727a89;text-transform:uppercase}
div[data-testid="stSidebar"]{background:#090b10;border-right:1px solid var(--line)}
hr{border-color:var(--line)}
@media(max-width:800px){.hero-title{font-size:45px}.glass{padding:18px}.orb{margin:25px auto}.ticket-grid{grid-template-columns:1fr 1fr}}
</style>
""", unsafe_allow_html=True)


# ---------------- SMART REQUEST PARSER ----------------
def parse_request(text):
    import re
    t = (text or "").lower()
    destination = None
    destination_map = {
        "america": "New York, USA", "usa": "New York, USA",
        "united states": "New York, USA", "new york": "New York, USA",
        "california": "Los Angeles, USA", "los angeles": "Los Angeles, USA",
        "dubai": "Dubai, UAE", "london": "London, UK", "paris": "Paris, France",
        "istanbul": "Istanbul, Türkiye", "karachi": "Karachi, Pakistan",
        "lahore": "Lahore, Pakistan", "islamabad": "Islamabad, Pakistan",
    }
    for key, value in destination_map.items():
        if key in t:
            destination = value
            break
    people = None
    m = re.search(r'(\d+)\s*(?:person|people|persons|travell?ers?|pax)', t)
    if m: people = int(m.group(1))
    elif "couple" in t or "for two" in t: people = 2
    days = None
    m = re.search(r'(\d+)\s*(?:day|days)', t)
    if m: days = int(m.group(1))
    budget = None
    m = re.search(r'(?:under|below|budget(?: of)?|within)\s*(?:rs\.?|pkr)?\s*([\d,]+)', t)
    if m: budget = int(m.group(1).replace(",", ""))
    return destination, people, days, budget

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
        st.markdown("### COMMAND CENTER")
        if st.button("⌂  Overview",use_container_width=True): go("dashboard")
        if st.button("＋  New plan",use_container_width=True): go("create")
        st.divider()
        st.caption("CORE STATUS")
        st.success("AI Core Online")
    logo()
    st.markdown('<div class="eyebrow"><span class="pulse"></span>AEGIS COMMAND CENTER</div><div class="hero-title" style="font-size:50px">Your intelligence<br><span>workspace.</span></div><p class="muted">Create an objective, then open each intelligence module to inspect the plan in detail.</p>',unsafe_allow_html=True)

    prompt=st.text_input("Command",placeholder="e.g. Plan a 5-day trip to America for 4 people under Rs. 800,000",label_visibility="collapsed")
    if st.button("✦  Create plan",use_container_width=True):
        st.session_state.prompt=prompt or "Plan a 5-day trip to America for 4 people under Rs. 800,000"
        go("create")

    st.write("")
    if st.session_state.plan:
        p=st.session_state.plan
        st.markdown(f'<div class="glass"><div class="smallcaps">ACTIVE PLAN</div><h2>{p["city"]} · {p["days"]} days · {p["people"]} travelers</h2><span class="tag">BUDGET · Rs. {p["budget"]:,}</span><span class="tag">AEGIS SCORE · 91</span></div>',unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="smallcaps">INTELLIGENCE MODULES</div><h2>Open a module</h2>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    modules=[(c1,"flights","✈","Flights","Open ticket, route, timings, baggage and passenger details."),(c2,"hotel","⌂","Hotel","Open room, nights, check-in/out, amenities and selection logic."),(c3,"itinerary","◷","Itinerary","Open the complete day-by-day schedule and route logic.")]
    for col,key,icon,title,sub in modules:
        with col:
            st.markdown(f'<div class="glass module"><div class="module-icon">{icon}</div><div class="module-title">{title}<span class="module-arrow">↗</span></div><div class="module-sub">{sub}</div></div>',unsafe_allow_html=True)
            if st.button(f"Open {title}",key="open_"+key,use_container_width=True):
                st.session_state.module=key;go("module")
    c1,c2,c3=st.columns(3)
    modules2=[(c1,"budget","₨","Budget","Inspect every estimated cost and remaining budget."),(c2,"reasoning","◎","AI Reasoning","See the decision chain behind the recommendations."),(c3,"whatif","↻","What-If","Change constraints and re-optimize the plan.")]
    for col,key,icon,title,sub in modules2:
        with col:
            st.markdown(f'<div class="glass module"><div class="module-icon">{icon}</div><div class="module-title">{title}<span class="module-arrow">↗</span></div><div class="module-sub">{sub}</div></div>',unsafe_allow_html=True)
            if st.button(f"Open {title}",key="open2_"+key,use_container_width=True):
                if key=="whatif": go("whatif")
                else: st.session_state.module=key;go("module")
# ---------------- CREATE ----------------
elif st.session_state.screen=="create":
    logo()
    st.markdown(
        '<div class="eyebrow">✦ NEW PLAN</div>'
        '<div class="hero-title" style="font-size:48px">Tell AEGIS what you want.</div>'
        '<p class="muted">One objective is enough. AEGIS extracts the destination, travelers, duration and budget automatically.</p>',
        unsafe_allow_html=True
    )

    default = getattr(
        st.session_state,
        "prompt",
        "Plan a 5-day trip to America for 4 people under Rs. 800,000"
    )

    st.markdown('<div class="glass"><div class="smallcaps">YOUR OBJECTIVE</div>', unsafe_allow_html=True)
    prompt = st.text_area(
        "Objective",
        value=default,
        height=135,
        placeholder="Example: Plan a 5-day trip to America for 4 people under Rs. 800,000",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    detected_city, detected_people, detected_days, detected_budget = parse_request(prompt)
    detected_city = detected_city or "Destination to be researched"
    detected_people = detected_people or 2
    detected_days = detected_days or 2
    detected_budget = detected_budget or 50000

    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">AEGIS UNDERSTANDING</div><h3>Here is what I understood</h3>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    cards = [
        ("DESTINATION", detected_city),
        ("TRAVELERS", str(detected_people)),
        ("DURATION", f"{detected_days} days"),
        ("BUDGET", f"Rs. {detected_budget:,}")
    ]
    for col,(title,value) in zip([c1,c2,c3,c4],cards):
        with col:
            st.markdown(f'<div class="metric"><small>{title}</small><b style="font-size:19px">{value}</b></div>', unsafe_allow_html=True)
    st.markdown('<p class="muted" style="margin-top:14px">No second form. If something is wrong, simply edit the objective above.</p></div>', unsafe_allow_html=True)

    st.write("")
    if st.button("✦  Run AEGIS", use_container_width=True):
        st.session_state.plan = {
            "city": detected_city,
            "days": detected_days,
            "people": detected_people,
            "budget": detected_budget,
            "prompt": prompt
        }
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
    p = st.session_state.plan or {"city":"Karachi","days":2,"people":2,"budget":50000}
    city = p["city"]
    days = int(p["days"])
    people = int(p["people"])
    nights = max(1, days - 1)
    budget = int(p["budget"])

    is_usa = "usa" in city.lower()
    if "new york" in city.lower():
        hotel = "The Manhattan Grand · Deluxe King Room"
        outbound = "AEGIS Air AX-701"
        return_f = "AEGIS Air AX-702"
        route_out = "Islamabad (ISB) → New York (JFK)"
        route_back = "New York (JFK) → Islamabad (ISB)"
        out_time = "22:40 — 06:15 (+1)"
        back_time = "21:20 — 05:10 (+1)"
        activities = ["Times Square & Broadway District","Central Park","Statue of Liberty / Downtown","5th Avenue & Hudson River"]
    elif "los angeles" in city.lower():
        hotel = "West Hollywood Residence · Premium Room"
        outbound = "AEGIS Air AX-611"
        return_f = "AEGIS Air AX-612"
        route_out = "Islamabad (ISB) → Los Angeles (LAX)"
        route_back = "Los Angeles (LAX) → Islamabad (ISB)"
        out_time = "23:10 — 07:20 (+1)"
        back_time = "20:45 — 04:55 (+1)"
        activities = ["Hollywood Boulevard","Santa Monica Pier","Griffith Observatory","Beverly Hills"]
    else:
        hotel = f"{city} Central Hotel · Deluxe Room"
        outbound = "AEGIS Air AX-214"
        return_f = "AEGIS Air AX-219"
        route_out = f"Origin → {city}"
        route_back = f"{city} → Origin"
        out_time = "08:20 — 10:15"
        back_time = "20:10 — 22:05"
        activities = ["Top cultural attraction","Central city district","Local food experience","Sunset / leisure activity"]

    rooms = max(1, math.ceil(people/2))
    flight_total = 18000 * people
    hotel_total = 8000 * nights * rooms
    transport_total = 2400 * people
    food_total = 1800 * people * days
    activity_total = 1000 * people * days
    estimated_total = flight_total + hotel_total + transport_total + food_total + activity_total

    st.markdown(
        f'<div class="eyebrow"><span class="pulse"></span>PLAN READY · AEGIS OPTIMIZED</div>'
        f'<div class="hero-title" style="font-size:46px">{city} Getaway</div>'
        f'<p class="muted">Complete plan for <b>{people} travelers</b> · {days} days · {nights} nights.</p>',
        unsafe_allow_html=True
    )

    a,b,c,d = st.columns(4)
    for col,title,val in zip(
        [a,b,c,d],
        ["OPTIMIZATION SCORE","ESTIMATED TOTAL","STAY","TRAVELERS"],
        ["91 / 100",f"Rs. {estimated_total:,}",f"{days} days / {nights} nights",str(people)]
    ):
        with col:
            st.markdown(f'<div class="metric"><small>{title}</small><b>{val}</b></div>',unsafe_allow_html=True)

    st.write("")
    left,right = st.columns([1.08,.92],gap="large")

    with left:
        st.markdown('<div class="glass"><div class="smallcaps">FLIGHTS</div><h2>✈ Selected flights</h2>',unsafe_allow_html=True)
        st.markdown(f"""
        <div class="reason"><b>Outbound · {outbound}</b><p>{route_out} · {out_time} · Economy · {people} travelers</p></div>
        <div class="reason"><b>Return · {return_f}</b><p>{route_back} · {back_time} · Economy · {people} travelers</p></div>
        <div style="display:flex;justify-content:space-between;font-size:10px;margin-top:14px"><span>Estimated flight cost</span><b>Rs. {flight_total:,}</b></div>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="glass"><div class="smallcaps">HOTEL</div><h2>⌂ Selected accommodation</h2>',unsafe_allow_html=True)
        st.markdown(f"""
        <div class="reason"><b>{hotel}</b>
        <p>{rooms} room(s) · {people} travelers · Check-in Day 1 at 14:00</p>
        <p>Check-out Day {days} at 12:00 · {nights} night(s) · Breakfast included</p></div>
        <div style="display:flex;justify-content:space-between;font-size:10px;margin-top:14px"><span>Estimated hotel cost</span><b>Rs. {hotel_total:,}</b></div>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass"><div class="smallcaps">TRIP SNAPSHOT</div><h2>Stay & schedule</h2>',unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric" style="margin-bottom:10px"><small>DESTINATION</small><b>{city}</b></div>
        <div class="metric" style="margin-bottom:10px"><small>CHECK-IN</small><b>DAY 1 · 14:00</b></div>
        <div class="metric" style="margin-bottom:10px"><small>CHECK-OUT</small><b>DAY {days} · 12:00</b></div>
        <div class="metric"><small>ROOMS</small><b>{rooms}</b></div>
        """,unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

        st.write("")
        st.markdown(f'<div class="glass"><div class="smallcaps">BUDGET BREAKDOWN</div><h2>Rs. {estimated_total:,}</h2>',unsafe_allow_html=True)
        for label,value in [("Flights",flight_total),("Hotel",hotel_total),("Transport",transport_total),("Food",food_total),("Activities",activity_total)]:
            pct=min(100,value/max(1,estimated_total)*100)
            st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:10px"><span>{label}</span><span>Rs. {value:,}</span></div><div class="progress-wrap" style="margin:6px 0 12px"><div class="progress-bar" style="width:{pct}%"></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">DAY-BY-DAY PLAN</div><h2>Customer itinerary</h2>',unsafe_allow_html=True)
    for day in range(1,days+1):
        if day == 1:
            detail = f"Arrival · hotel check-in · {activities[0]} · dinner"
        elif day == days:
            detail = f"Breakfast · {activities[min(2,len(activities)-1)]} · leisure · airport transfer"
        else:
            detail = f"Breakfast · {activities[(day-1) % len(activities)]} · lunch · {activities[day % len(activities)]} · dinner"
        st.markdown(f'<div class="reason"><b>DAY {day}</b><p>{detail}</p></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="glass"><div class="smallcaps">AI REASONING</div><h2>Why AEGIS selected this plan</h2>',unsafe_allow_html=True)
    for title,txt in [
        ("✈ Flights","Timing is selected to maximize usable destination time while keeping the return practical."),
        ("⌂ Hotel","Hotel choice is matched to the destination, stay length, traveler count and planning priority."),
        ("↗ Stay","Room count and nights are calculated from the requested traveler count and duration."),
        ("◇ Activities","Activities are distributed across days to reduce unnecessary backtracking."),
        ("₨ Budget","Every major cost is visible so the customer can understand where the money goes.")
    ]:
        st.markdown(f'<div class="reason"><b>{title}</b><p>{txt}</p></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.write("")
    c1,c2=st.columns(2)
    with c1:
        if st.button("↻  What If? Optimize",use_container_width=True): go("whatif")
    with c2:
        if st.button("←  Back to Command Center",use_container_width=True): go("dashboard")


# ---------------- MODULES ----------------
elif st.session_state.screen=="module":
    p=st.session_state.plan or {"city":"New York, USA","days":5,"people":4,"budget":800000}
    city=p["city"]; days=int(p["days"]); people=int(p["people"]); nights=max(1,days-1); budget=int(p["budget"])
    module=st.session_state.get("module","overview")

    if st.button("← Back to plan overview"):
        go("workspace")
    logo()

    if module=="flights":
        st.markdown('<div class="eyebrow">✦ TRANSPORT MODULE · DEMO ESTIMATE</div><div class="hero-title" style="font-size:48px">Your flight plan.</div><p class="muted">Selected around your traveler count, schedule and destination. Prices shown are demo estimates until a live flight provider is connected.</p>',unsafe_allow_html=True)
        st.markdown(f'<div class="ticket"><div class="ticket-top"><div class="ticket-brand">AEGIS TRAVEL INTELLIGENCE</div><div class="ticket-code">DEMO TICKET · AX-701</div></div><div style="margin-top:22px"><span class="airport">ISB</span><span style="padding:0 22px;color:#6a637d">✈ ───────── ✈</span><span class="airport">JFK</span></div><div class="ticket-code" style="margin-top:4px">ISLAMABAD → NEW YORK</div><div class="flightline"></div><div class="ticket-grid"><div><div class="ticket-label">Departure</div><div class="ticket-value">22:40 · ISB</div></div><div><div class="ticket-label">Arrival</div><div class="ticket-value">06:15 +1 · JFK</div></div><div><div class="ticket-label">Passengers</div><div class="ticket-value">{people} travelers</div></div><div><div class="ticket-label">Cabin</div><div class="ticket-value">Economy</div></div><div><div class="ticket-label">Baggage</div><div class="ticket-value">1 × 23kg</div></div><div><div class="ticket-label">Flight</div><div class="ticket-value">AX-701</div></div></div><div class="barcode"></div></div>',unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="glass"><div class="smallcaps">RETURN</div><h3>AX-702 · New York → Islamabad</h3><p class="muted">JFK 21:20 → ISB 05:10 (+1) · Economy · {0} travelers · Estimated round-trip package: Rs. {1:,}</p></div>'.format(people,18000*people),unsafe_allow_html=True)

    elif module=="hotel":
        rooms=max(1,math.ceil(people/2)); hotel_total=8000*nights*rooms
        st.markdown('<div class="eyebrow">✦ ACCOMMODATION MODULE · DEMO ESTIMATE</div><div class="hero-title" style="font-size:48px">Your stay.</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="hotel-card"><div class="hotel-visual"><span>MANHATTAN · CENTRAL LOCATION · 4.5/5</span></div><div style="padding:20px"><h2 style="margin:0">The Manhattan Grand</h2><p class="muted">Deluxe King Room · {rooms} room(s) · Breakfast included</p><div class="ticket-grid"><div><div class="ticket-label">Check-in</div><div class="ticket-value">Day 1 · 14:00</div></div><div><div class="ticket-label">Check-out</div><div class="ticket-value">Day {days} · 12:00</div></div><div><div class="ticket-label">Nights</div><div class="ticket-value">{nights}</div></div></div><hr><div class="reason"><b>Why AEGIS picked it</b><p>Central location reduces daily travel, room count matches {people} travelers, and breakfast protects the food budget.</p></div><b>Estimated stay · Rs. {hotel_total:,}</b></div></div>',unsafe_allow_html=True)

    elif module=="itinerary":
        st.markdown('<div class="eyebrow">✦ ITINERARY MODULE</div><div class="hero-title" style="font-size:48px">Every day, mapped.</div><p class="muted">AEGIS groups activities by area and time to reduce backtracking.</p>',unsafe_allow_html=True)
        activities=["Arrival + Midtown orientation","Central Park + Museum District","Statue of Liberty + Downtown","5th Avenue + Hudson River","Flexible final day + airport transfer"]
        for day in range(1,days+1):
            title=activities[(day-1)%len(activities)]
            st.markdown(f'<div class="glass"><div class="smallcaps">DAY {day}</div><h3>{title}</h3><div class="timeline"><div class="titem"><b>08:00 · Breakfast</b><small>Hotel breakfast</small></div><div class="titem"><b>10:00 · Main activity</b><small>High-priority experience</small></div><div class="titem"><b>13:30 · Lunch</b><small>Nearby dining to minimize transit</small></div><div class="titem"><b>15:30 · Secondary activity</b><small>Flexible based on energy and weather</small></div><div class="titem"><b>20:00 · Dinner</b><small>Return toward hotel area</small></div></div></div>',unsafe_allow_html=True)

    elif module=="budget":
        flight=18000*people; hotel=8000*nights*max(1,math.ceil(people/2)); transport=2400*people; food=1800*people*days; activities=1000*people*days; total=flight+hotel+transport+food+activities
        st.markdown('<div class="eyebrow">✦ BUDGET MODULE</div><div class="hero-title" style="font-size:48px">Where the money goes.</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="metric"><small>USER LIMIT</small><b>Rs. {budget:,}</b><span style="color:#68e3a0;font-size:9px">Estimated spend: Rs. {total:,} · Remaining: Rs. {max(0,budget-total):,}</span></div>',unsafe_allow_html=True)
        for label,value in [("Flights",flight),("Hotel",hotel),("Local transport",transport),("Food",food),("Activities",activities)]:
            pct=min(100,value/max(1,total)*100)
            st.markdown(f'<div class="glass" style="margin-top:10px;padding:16px"><div style="display:flex;justify-content:space-between;font-size:10px"><b>{label}</b><b>Rs. {value:,}</b></div><div class="progress-wrap" style="margin-top:9px"><div class="progress-bar" style="width:{pct}%"></div></div></div>',unsafe_allow_html=True)

    elif module=="reasoning":
        st.markdown('<div class="eyebrow">✦ DECISION INTELLIGENCE</div><div class="hero-title" style="font-size:48px">See inside the decision.</div><p class="muted">This is the reasoning layer of the demo — what an examiner can inspect instead of seeing a black-box answer.</p>',unsafe_allow_html=True)
        for n,title,txt in [
            ("01","Constraint extraction",f"AEGIS identified {people} travelers, {days} days and a maximum budget of Rs. {budget:,}."),
            ("02","Flight trade-off","Departure/arrival timing was weighted against usable destination time and traveler count."),
            ("03","Hotel trade-off","Location, room capacity, nights and breakfast were balanced against the budget."),
            ("04","Route optimization","Activities are grouped by geography so the plan avoids unnecessary backtracking."),
            ("05","Budget protection","The system keeps the major costs visible and preserves a contingency margin.")
        ]:
            st.markdown(f'<div class="glass" style="margin-bottom:10px"><div class="eyebrow">{n}</div><h3>{title}</h3><p class="muted">{txt}</p></div>',unsafe_allow_html=True)
    else:
        st.info("Module not found.")

# ---------------- WHAT IF ----------------
elif st.session_state.screen=="whatif":
    p=st.session_state.plan or {"city":"Karachi","days":2,"people":2,"budget":50000}
    logo()
    st.markdown('<div class="eyebrow">◈ SCENARIO SIMULATOR</div><div class="hero-title" style="font-size:48px">What if we change the rules?</div><p class="muted">Adjust a constraint and let AEGIS re-optimize the plan.</p>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: nb=st.number_input("Budget (Rs.)",1000,1000000,max(1000,int(p["budget"])),step=5000)
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
