import os
OUT=os.path.dirname(os.path.abspath(__file__))
SK={ # semantic roles from diagram-design style-guide.md (default skin)
 "light":dict(paper="#f5f5f5",paper2="#ececec",ink="#2d3142",inkc="45,49,66",muted="#4f5d75",soft="#5a6580",accent="#bf4520",accentc="191,69,32",link="#2e5aa8",white="#ffffff"),
 "dark":dict(paper="#2d3142",paper2="#393e53",ink="#f5f5f5",inkc="245,245,245",muted="#bfc0c0",soft="#949eb2",accent="#f08a59",accentc="240,138,89",link="#739fdf",white="#393e53")}
FONTS='<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">'
def page(T,slug,eyebrow,h1,svg):
    t=SK[T]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{h1}</title>
  {FONTS}
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ --color-paper:{t['paper']}; --color-ink:{t['ink']}; --color-muted:{t['muted']}; --color-accent:{t['accent']};
      --font-sans:'Geist', system-ui, sans-serif; --font-serif:'Instrument Serif', 'Noto Serif', serif; --font-mono:'Geist Mono', ui-monospace, monospace; }}
    body {{ font-family:var(--font-sans); background:var(--color-paper); color:var(--color-ink); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:3rem 2rem; }}
    .frame {{ max-width:1200px; width:100%; }}
    .diagram-container {{ width:100%; overflow-x:auto; }}
    .eyebrow {{ font-family:var(--font-mono); font-size:0.66rem; font-weight:500; letter-spacing:0.18em; text-transform:uppercase; color:var(--color-muted); margin-bottom:0.5rem; }}
    h1 {{ font-family:var(--font-serif); font-size:clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight:400; letter-spacing:-0.02em; line-height:1.15; color:var(--color-ink); margin-bottom:1.5rem; }}
    svg {{ width:100%; min-width:960px; display:block; }}
    @media print {{ .diagram-container {{ overflow-x:visible; }} svg {{ min-width:0; }} }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <div class="diagram-container">
{svg}
    </div>
  </div>
</body>
</html>
'''
def defs(t,slug): return f'''<defs>
          <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{t['muted']}"/></marker>
          <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{t['accent']}"/></marker>
          <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{t['link']}"/></marker>
        </defs>'''
def rgba(c,a): return f"rgba({c},{a})"
def fills(kind,t):
    ic,ac=t['inkc'],t['accentc']
    return {"focal":(rgba(ac,0.08 if t['paper']=="#f5f5f5" else 0.10),t['accent'],None),
            "backend":(t['white'],t['ink'],None),
            "store":(rgba(ic,0.05),t['muted'],None),
            "external":(rgba(ic,0.03),rgba(ic,0.30),None),
            "input":(rgba("79,93,117" if t['paper']=="#f5f5f5" else "191,192,192",0.10),t['soft'],None)}[kind]
def node(t,x,y,w,h,kind,tag,name,sub):
    f,s,_=fills(kind,t); tg=t['muted'] if kind in ('external','store') else s; cx=x+w/2; tw=int(len(tag)*5.4+12)//4*4+4
    return f'''<g>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{t['paper']}"/>
          <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{f}" stroke="{s}" stroke-width="1"/>
          <rect x="{x+8}" y="{y+8}" width="{tw}" height="12" rx="2" fill="transparent" stroke="{tg}" stroke-opacity="0.55" stroke-width="0.8"/>
          <text x="{x+8+tw/2}" y="{y+17}" fill="{tg}" font-size="7" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.08em">{tag}</text>
          <text x="{cx}" y="{y+46}" fill="{t['ink']}" font-size="12" font-weight="600" font-family="'Geist', system-ui, sans-serif" text-anchor="middle">{name}</text>
          <text x="{cx}" y="{y+62}" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle">{sub}</text>
        </g>'''
def label(t,cx,y,txt,w=None):
    w=w or int(len(txt)*5.2+14)//4*4+4; x=cx-w/2
    return f'''<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="{t['paper']}"/>
          <text x="{cx}" y="{y+9}" fill="{t['soft']}" font-size="8" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.06em">{txt}</text>'''
def path(d,color="muted",dash=False,marker=None):
    m={"muted":"arrow","accent":"arrow-accent","link":"arrow-link"}[color]
    return f'<path d="{d}" fill="none" stroke="{{{color}}}" stroke-width="1.2"{" stroke-dasharray=\"4,3\"" if dash else ""} marker-end="url(#{m})"/>'
def arch(T):
    t=SK[T]; slug="architecture"+("-dark" if T=="dark" else "")
    def P(d,c="muted"): return path(d,c).replace("{muted}",t['muted']).replace("{accent}",t['accent']).replace("{link}",t['link'])
    zone=lambda x,y,w,h,txt:f'''<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{rgba(t['inkc'],0.02)}" stroke="{rgba(t['inkc'],0.10)}" stroke-width="0.8"/>
          <rect x="{x+w/2-28}" y="{y+8}" width="56" height="12" rx="2" fill="{t['paper']}"/>
          <text x="{x+w/2}" y="{y+17}" fill="{t['soft']}" font-size="7" font-family="'Geist Mono', ui-monospace, monospace" text-anchor="middle" letter-spacing="0.14em">{txt}</text>'''
    arrows=[
     P("M208,330 H264","accent"),
     P("M440,317 H458 Q466,317 466,309 V208 Q466,200 474,200 H520"),
     P("M440,343 H474 Q482,343 482,351 V452 Q482,460 490,460 H520"),
     P("M744,200 H816","link"),
     P("M616,240 V309 Q616,317 624,317 H816","link"),
     P("M664,420 V351 Q664,343 672,343 H816","link"),
     P("M900,240 V290"),
     P("M984,200 H1056"),
     P("M984,330 H1136 Q1144,330 1144,322 V240"),
     P("M900,370 V450"),
     P("M984,490 H1056")]
    labels=[label(t,236,308,"ASK"),label(t,780,178,"CAD"),label(t,720,299,"RIG"),label(t,744,349,"RENDER"),label(t,926,258,"MESH",40),
            label(t,1020,178,"STEP"),label(t,1060,308,".BLEND",48),label(t,932,404,"FRAMES",52),label(t,1020,468,"ENCODE",52)]
    nodes=[node(t,48,290,160,80,"input","USER","Your request","a real mechanism"),
           node(t,264,290,176,80,"focal","GATES","mechanism-studio","orchestrator, 3 approvals"),
           node(t,520,160,224,80,"backend","SKILL","accurate-3d-modeling","sourced specs, CAD, rig"),
           node(t,520,420,224,80,"backend","SKILL","mechanism-animation-render","storyboard, render, cut"),
           node(t,816,160,168,80,"external","TOOL","FreeCAD","exact CAD, STEP, STL"),
           node(t,816,290,168,80,"external","TOOL","Blender","rig, materials, EEVEE"),
           node(t,816,450,168,80,"external","TOOL","ffmpeg","alpha and 9:16 encode"),
           node(t,1056,160,176,80,"store","OUTPUT","Model files","STEP, parts.csv, .blend"),
           node(t,1056,450,176,80,"store","OUTPUT","Media","30 s loop, alpha, 9:16")]
    leg=f'''<line x1="48" y1="584" x2="1232" y2="584" stroke="{rgba(t['inkc'],0.10)}" stroke-width="0.8"/>
          <text x="48" y="608" fill="{t['muted']}" font-size="8" font-family="'Geist Mono', ui-monospace, monospace" letter-spacing="0.14em">LEGEND</text>
          <rect x="124" y="599" width="14" height="12" rx="3" fill="{fills('focal',t)[0]}" stroke="{t['accent']}"/><text x="146" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Orchestrator</text>
          <rect x="248" y="599" width="14" height="12" rx="3" fill="{fills('backend',t)[0]}" stroke="{t['ink']}"/><text x="270" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Skill</text>
          <rect x="332" y="599" width="14" height="12" rx="3" fill="{fills('external',t)[0]}" stroke="{fills('external',t)[1]}"/><text x="354" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Tool</text>
          <rect x="416" y="599" width="14" height="12" rx="3" fill="{fills('store',t)[0]}" stroke="{t['muted']}"/><text x="438" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Output</text>
          <line x1="528" y1="605" x2="552" y2="605" stroke="{t['link']}" stroke-width="1.2" marker-end="url(#arrow-link)"/><text x="562" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Skill drives tool</text>
          <line x1="712" y1="605" x2="736" y2="605" stroke="{t['muted']}" stroke-width="1.2" marker-end="url(#arrow)"/><text x="746" y="609" fill="{t['muted']}" font-size="9" font-family="'Geist Mono', ui-monospace, monospace">Files and frames</text>'''
    svg=f'''<svg viewBox="0 96 1280 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">Mechanism skills architecture</title>
        <desc id="{slug}-desc">A request goes to an orchestrator skill that runs a modeling skill and an animation skill, which drive FreeCAD, Blender and ffmpeg to produce model files and media.</desc>
        {defs(t,slug)}
        <rect width="100%" height="100%" fill="{t['paper']}"/>
        {zone(500,124,264,424,"SKILLS")}
        {zone(796,124,208,424,"TOOLS")}
        {chr(10).join("        "+a for a in arrows)}
        {chr(10).join("        "+l for l in labels)}
        {chr(10).join("        "+n for n in nodes)}
        {leg}
      </svg>'''
    return page(T,slug,"Architecture · Mechanism skills","Three skills turn a real mechanism into model files and media",svg)
def steps(T):
    t=SK[T]; slug="steps"+("-dark" if T=="dark" else ""); ic,ac=t['inkc'],t['accentc']
    S=[("01","Research",["Sourced specs, parts list","approved by you"],'<path d="M3 10a7 7 0 1 0 14 0a7 7 0 1 0 -14 0" /> <path d="M21 21l-6 -6" />'),
       ("02","Model",["Exact CAD, kinematics and","interference checked"],'<path d="M14 3v4a1 1 0 0 0 1 1h4" /> <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2" />'),
       ("03","Storyboard",["Scenes on a page; you","approve, then say go"],'<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0" /> <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />'),
       ("04","Check",["Loop math, casing off","screen, disk and RAM"],'<path d="M20 8.04l-12.122 12.124a2.857 2.857 0 1 1 -4.041 -4.04l12.122 -12.124" /> <path d="M7 13h8" /> <path d="M19 15l1.5 1.6a2 2 0 1 1 -3 0l1.5 -1.6" /> <path d="M15 3l6 6" />'),
       ("05","Render",["Chunked, RAM-guarded,","every frame validated"],'<path d="M5 18a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M5 6a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M15 12a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" /> <path d="M7 8l0 8" /> <path d="M7 8a4 4 0 0 0 4 4h4" />'),
       ("06","Deliver",["Alpha, opaque and","vertical 9:16 files"],'<path d="M4 7a8 4 0 1 0 16 0a8 4 0 1 0 -16 0" /> <path d="M4 7c0 .664 .088 1.324 .263 1.965l2.737 10.035c.5 1.5 2.239 2 5 2s4.5 -.5 5 -2c.333 -1 1.246 -4.345 2.737 -10.035a7.45 7.45 0 0 0 .263 -1.965" />')]
    n=len(S); sw=184; sx0=(1280-n*sw)//2; FOC=2
    mono="'Geist Mono', ui-monospace, monospace"; sans="'Geist', system-ui, sans-serif"
    rails="".join(f'<rect x="{sx0+i*sw}" y="240" width="{sw}" height="48" fill="{rgba(ac,0.08) if i==FOC else rgba(ic,0.05 if i%2==0 else 0.09)}" data-role="rail" data-step="{S[i][1].lower()}" data-index="{i+1}"{" data-focal=\"true\"" if i==FOC else ""}/>' for i in range(n))
    focal_rules=f'<line x1="{sx0+FOC*sw}" y1="240" x2="{sx0+(FOC+1)*sw}" y2="240" stroke="{t["accent"]}" stroke-width="1"/><line x1="{sx0+FOC*sw}" y1="288" x2="{sx0+(FOC+1)*sw}" y2="288" stroke="{t["accent"]}" stroke-width="1"/>'
    nums="".join(f'<text x="{sx0+i*sw+sw/2}" y="164" fill="{t["accent"] if i==FOC else t["muted"]}" data-role="number" data-step="{S[i][1].lower()}">{S[i][0]}</text>' for i in range(n))
    guides="".join(f'<line x1="{sx0+i*sw+sw/2}" y1="184" x2="{sx0+i*sw+sw/2}" y2="220" stroke="{t["accent"] if i==FOC else rgba(ic,0.25)}" stroke-width="1"/>' for i in range(n))
    meds=""
    for i in range(n):
        cx=sx0+i*sw+sw/2; foc=i==FOC
        meds+=f'<circle cx="{cx}" cy="264" r="36" stroke="none"/>'
        meds+=f'<circle cx="{cx}" cy="264" r="36" fill="{rgba(ac,0.08) if foc else t["paper"]}" stroke="{t["accent"] if foc else t["ink"]}" data-role="medallion" data-step="{S[i][1].lower()}"{" data-focal=\"true\"" if foc else ""}/>'
    icons="".join(f'<g transform="translate({sx0+i*sw+sw/2-12},252)" color="{t["accent"] if i==FOC else t["ink"]}" aria-hidden="true"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{S[i][3]}</svg></g>' for i in range(n))
    copy=""
    for i in range(n):
        cx=sx0+i*sw+sw/2
        copy+=f'<text x="{cx}" y="360" fill="{t["accent"] if i==FOC else t["ink"]}" font-size="12" font-weight="600" font-family="{sans}" text-anchor="middle">{S[i][1]}</text>'
        for j,l in enumerate(S[i][2]): copy+=f'<text x="{cx}" y="{388+20*j}" fill="{t["muted"]}" font-size="9" font-family="{mono}" text-anchor="middle">{l}</text>'
    # gate callouts under the rail: three approval points
    gates=[(0.0,"you approve parts"),(2.0,"you approve scenes"),(2.5,"you say go")]
    leg=f'''<line x1="80" y1="600" x2="1200" y2="600" stroke="{rgba(ic,0.10)}" stroke-width="0.8"/>
          <circle cx="104" cy="628" r="7" fill="{t['paper']}" stroke="{t['ink']}"/><text x="120" y="632" fill="{t['muted']}" font-size="9" font-family="{mono}">Stage</text>
          <circle cx="204" cy="628" r="7" fill="{rgba(ac,0.08)}" stroke="{t['accent']}"/><text x="220" y="632" fill="{t['muted']}" font-size="9" font-family="{mono}">Where you decide before any long render</text>
          <text x="1200" y="634" fill="{t['muted']}" font-size="14" font-style="italic" font-family="'Instrument Serif', 'Noto Serif', serif" text-anchor="end">Equal spacing shows order, not elapsed time.</text>'''
    svg=f'''<svg viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">From a real mechanism to finished media</title>
        <desc id="{slug}-desc">Six steps on one rail: research, model, storyboard, check, render and deliver; the storyboard step is where you approve before the long render.</desc>
        <rect width="100%" height="100%" fill="{t['paper']}"/>
        <g aria-hidden="true">{rails}</g>
        {focal_rules}
        <g font-family="{mono}" font-size="8" font-weight="600" letter-spacing="0.14em" text-anchor="middle">{nums}</g>
        {guides}
        <g aria-hidden="true" fill="{t['paper']}" stroke-width="1">{meds}</g>
        {icons}
        {copy}
        {leg}
      </svg>'''
    return page(T,slug,"Steps · Mechanism skills","From a real mechanism to finished media in six steps",svg)
for T in ("light","dark"):
    open(os.path.join(OUT,f"architecture-{T}.html"),"w").write(arch(T))
    open(os.path.join(OUT,f"steps-{T}.html"),"w").write(steps(T))
print("ok",os.listdir(OUT))
