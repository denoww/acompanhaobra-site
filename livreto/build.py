#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o livreto do acompanhaobra → livreto/index.html (rota /livreto).

    python3 livreto/build.py

Doutrina herdada do livreto do SeuCondomínio (~/workspace/seucondominio/livreto/CLAUDE.md):
  - Long-scroll Apple, capítulos alternando branco/névoa, storyboards de fluxo.
  - Selo só onde é verdade. Nunca vender roadmap como pronto → capítulo "O que ele não faz".
  - NUNCA editar o HTML gerado. Edita-se `content.py` (95% das mudanças) ou este arquivo.

Diferença de infra: o SeuCondomínio gera o PDF em RUNTIME (Gotenberg). Aqui o site é
estático (GitHub Pages, sem runtime), então o PDF é gerado no build por Chromium headless
(`livreto/build_pdf.sh`) e commitado. Rodar os dois ao mudar conteúdo.

PEGADINHAS DO PRINT (custaram correção no repo original — não mexer sem entender):
  - `@media print` PRECISA forçar `.rev{opacity:1}` — senão o PDF sai EM BRANCO.
  - `print-color-adjust:exact` — senão hero/CTA/fotos saem sem cor.
  - `break-inside:avoid` só nas unidades atômicas (card, painel). NUNCA por capítulo:
    gera páginas quase vazias.
  - Traço de SVG: usar `stroke` explícito no elemento. (No repo original, as classes
    utilitárias `.s`/`.w` forçavam `stroke:none` e o traço sumia calado.)
"""
import pathlib, importlib.util, datetime, hashlib

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
OUT  = REPO / "livreto" / "index.html"

sp = importlib.util.spec_from_file_location("content", str(ROOT / "content.py"))
C = importlib.util.module_from_spec(sp); sp.loader.exec_module(C)

WA = C.WA + C.WA_TXT

# --------------------------------------------------------------------- cenas
# Line-art dos storyboards. `stroke="currentColor"` explícito e fill="none" —
# nada de classe utilitária que possa zerar o traço.
# ⚠️ Traço: `stroke="currentColor"` + `fill="none"` são aplicados pelo `scene()` no <g>.
# NÃO usar classe utilitária aqui — no repo de origem as classes `.s`/`.w` forçavam
# `stroke:none` e o desenho sumia sem erro nenhum.
# As chaves têm que casar 1:1 com as cenas citadas em `content.py > BOARDS`.
SCENES = {
 # ── obra do condomínio ────────────────────────────────────────────────────
 "cotacao":  '<rect x="10" y="10" width="15" height="20" rx="2"/><rect x="31" y="10" width="15" height="20" rx="2"/>'
             '<path d="M14 17h7M14 22h7M35 17h7M35 22h7"/><path d="M22 36h12"/><path d="M31 33l3 3-3 3"/>',
 "contrato": '<rect x="15" y="7" width="26" height="30" rx="2"/><path d="M20 15h16M20 21h16M20 27h8"/>'
             '<path d="M28 33c2-3 4-3 6 0s4 3 6 0"/>',
 "etapas":   '<circle cx="14" cy="22" r="4"/><circle cx="28" cy="22" r="4"/><circle cx="42" cy="22" r="4"/>'
             '<path d="M18 22h6M32 22h6"/><path d="M12.5 22l1.2 1.2 2.3-2.4"/>',
 "diario":   '<rect x="16" y="9" width="24" height="29" rx="2"/>'
             '<path d="M23 6h10v5H23z"/>'
             '<path d="M21 20h14M21 26h14M21 32h9"/>'
             '<circle cx="36" cy="15" r="2.5"/>',
 "medicao":  '<rect x="11" y="14" width="34" height="17" rx="2"/><path d="M11 21h34"/>'
             '<path d="M17 14v7M23 14v7M29 14v7M35 14v7M39 14v7"/><path d="M17 26h13"/>',
 "termo":    '<rect x="15" y="7" width="26" height="30" rx="2"/><path d="M20 14h16M20 20h16"/>'
             '<circle cx="28" cy="29" r="6"/><path d="M25.5 29l1.8 1.8 3.7-3.8"/>',
 # ── reforma de unidade (NBR 16280) ────────────────────────────────────────
 "morador":  '<path d="M13 24L28 12l15 12"/><path d="M17 22v14h22V22"/><rect x="24" y="27" width="8" height="9"/>',
 "ia":       '<rect x="15" y="7" width="26" height="30" rx="2"/><path d="M20 15h16M20 21h11"/>'
             '<circle cx="34" cy="29" r="7"/><path d="M31 29h6M34 26v6"/>',
 "checklist":'<rect x="14" y="8" width="28" height="30" rx="2"/><path d="M26 16h11M26 23h11M26 30h7"/>'
             '<path d="M19 15l1.6 1.6 3-3.2"/><path d="M19 22l1.6 1.6 3-3.2"/><path d="M18.5 29.5l4 4M22.5 29.5l-4 4"/>',
 "assina":   '<path d="M12 33h32"/><path d="M17 28c4-8 7-12 9-12s1 8 3 8 4-6 7-6"/><circle cx="39" cy="18" r="3"/>',
 # ── fiscalização ──────────────────────────────────────────────────────────
 "foto":     '<rect x="11" y="15" width="34" height="22" rx="3"/><circle cx="28" cy="26" r="7"/>'
             '<path d="M22 15l2.5-4h7l2.5 4"/>',
 "prazo":    '<circle cx="28" cy="24" r="13"/><path d="M28 16v8l6 3.5"/><path d="M15 12v6h6"/>',
 "infracao": '<path d="M28 9l17 29H11z"/><path d="M28 20v9"/><circle cx="28" cy="33" r="1.4"/>',
}
def scene(n):
    return ('<svg class="scene" viewBox="0 0 56 44" aria-hidden="true">'
            f'<g fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round">{SCENES[n]}</g></svg>')

# ---------------------------------------------------------------- componentes
_CHAP = [0]
def chapter(cid, eyebrow, h2, lead, *blocks):
    bg = "nevoa" if _CHAP[0] % 2 else ""   # alterna sozinho — não passe bg
    _CHAP[0] += 1
    return f'''<section class="cap {bg}" id="{cid}" aria-label="{eyebrow}">
  <div class="cap-in">
    <div class="cap-head rev"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>
      {f'<p class="lead">{lead}</p>' if lead else ''}</div>
    {"".join(blocks)}
  </div>
</section>'''

def tag(t):
    return f'<span class="tg">{t}</span>' if t else ''

def cards(items, cor):
    cs = "".join(f'<article class="fc"><span class="fc-mk"></span><h3>{t}{tag(g)}</h3><p>{d}</p></article>'
                 for t, d, g in items)
    return f'<div class="fgrid c-{cor} rev">{cs}</div>'

def board(key):
    cor, titulo, panels = C.BOARDS[key]
    cells = []
    for i, (sc, h, cap) in enumerate(panels):
        cells.append(f'<li class="bp"><span class="bp-n">{i+1}</span>'
                     f'<span class="bp-art">{scene(sc)}</span><b>{h}</b><i>{cap}</i></li>')
        if i < len(panels) - 1:
            cells.append('<li class="bp-arr" aria-hidden="true">→</li>')
    return (f'<figure class="board c-{cor} rev"><figcaption class="board-cap">'
            f'<span class="eyebrow">Como funciona</span><b>{titulo}</b></figcaption>'
            f'<ol class="board-strip">{"".join(cells)}</ol></figure>')

def foto(slug, alt, extra=""):
    return (f'<figure class="shot{extra}"><img src="/assets/{slug}.jpg" alt="{alt}" '
            f'loading="lazy" decoding="async"></figure>')

def mrow(media, h, p, flip=False):
    return (f'<div class="mrow{" flip" if flip else ""} rev"><div class="m-media">{media}</div>'
            f'<div class="m-copy"><h3>{h}</h3><p>{p}</p></div></div>')

def lista(items):
    return ('<ul class="check rev">' +
            "".join(f'<li><span class="ck"></span>{t}</li>' for t in items) + '</ul>')

# ---------------------------------------------------------------------- CSS
CSS = """
:root{
  --branco:#fff;--nevoa:#f5f5f7;--preto:#000;
  --tinta:#1d1d1f;--tinta-2:#6e6e73;--claro:#f5f5f7;--claro-2:#a1a1a6;
  --terra:#B45309;--terra-vivo:#F59E0B;--terra-esc:#92400E;--terra-leve:#FBF0E2;
  --petroleo:#0F766E;--ciano:#0891B2;--ambar:#B45309;
  --linha:rgba(0,0,0,.12);--maxw:1120px;
  --sec:var(--terra);
  --ease:cubic-bezier(.45,0,.55,1);
}
.c-terra{--sec:#B45309;--soft:#FBF0E2}
.c-petroleo{--sec:#0F766E;--soft:#E0F2F1}
.c-ciano{--sec:#0891B2;--soft:#E0F3F7}
.c-ambar{--sec:#B45309;--soft:#FBF0E2}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--branco);color:var(--tinta);
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',system-ui,sans-serif;
  font-size:17px;line-height:1.4705882353;letter-spacing:-.022em;-webkit-font-smoothing:antialiased}
h1,h2,h3{margin:0;font-weight:600;line-height:1.06;letter-spacing:-.015em;text-wrap:balance}
p{margin:0}ul,ol{margin:0;padding:0;list-style:none}
a{color:var(--terra);text-decoration:none}
img{display:block;max-width:100%}
:focus-visible{outline:3px solid var(--terra-vivo);outline-offset:3px;border-radius:6px}
.eyebrow{display:block;font-size:21px;font-weight:600;letter-spacing:.011em;color:var(--sec);margin-bottom:8px}
.lead{font-size:21px;line-height:1.381;letter-spacing:.011em;color:var(--tinta-2);margin-top:14px}

.nav{position:sticky;top:0;z-index:50;height:52px;display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(20px,4vw,40px);background:rgba(255,255,255,.72);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(0,0,0,.08)}
.nav .brand{display:flex;align-items:center;gap:8px;font-weight:600;font-size:17px;color:var(--tinta);letter-spacing:-.02em}
.nav .brand img{width:24px;height:24px;border-radius:6px}
.nav .brand .tld{color:var(--terra)}
.nav-r{display:flex;align-items:center;gap:clamp(14px,3vw,26px);font-size:13px}
/* os <a> vivem DENTRO de .nav-links — sem display:flex aqui eles saem colados
   ("A batidaA prova"), porque o gap do .nav-r só separa os filhos diretos. */
.nav-links{display:inline-flex;align-items:center;gap:clamp(14px,2.2vw,24px)}
.nav-r a{color:var(--tinta);opacity:.85}
.nav-r a:hover{opacity:1;color:var(--terra)}
.nav-cta{background:var(--terra);color:#fff!important;padding:6px 14px;border-radius:980px;font-weight:500}
@media(max-width:760px){.nav-links{display:none}}

.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:var(--terra);color:#fff;
  padding:12px 22px;border-radius:980px;font-weight:400;font-size:17px;letter-spacing:-.022em;
  transition:background-color .1s linear}
.btn:hover{background:var(--terra-esc)}
.btn-branco{background:#fff;color:var(--tinta)}
.btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:32px}

/* hero */
.hero{background:var(--preto);color:var(--claro);text-align:center;padding:clamp(64px,9vh,104px) 24px 0;overflow:hidden;
  background-image:radial-gradient(900px 500px at 50% -10%,rgba(124,58,237,.5),transparent 62%)}
.hero .eyebrow{color:var(--terra-vivo)}
.hero h1{font-size:clamp(40px,4.4vw+14px,76px);color:#fff;max-width:16ch;margin:0 auto}
.hero .sub{margin:22px auto 0;max-width:56ch;font-size:21px;line-height:1.4;color:var(--claro-2);letter-spacing:.011em}
.hero-stage{margin:56px auto 0;max-width:900px}
/* banner: a foto sobe do hero e é cortada pelo fim da seção (o corte é de propósito).
   Sem aspect-ratio ela entra inteira e o corte cai em lugar aleatório. */
.hero-stage img{width:100%;aspect-ratio:16/8;object-fit:cover;object-position:60% 16%;
  border-radius:24px 24px 0 0;box-shadow:0 -10px 60px rgba(124,58,237,.3)}

.credo{max-width:960px;margin:0 auto;padding:clamp(80px,10vw,130px) 24px;text-align:center}
.credo h2{font-size:clamp(30px,3.4vw+10px,52px);letter-spacing:-.02em}
.credo .g{color:var(--terra)}

/* capítulos */
.cap{padding:clamp(72px,9vw,120px) 0}
.cap.nevoa{background:var(--nevoa)}
.cap-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.cap-head{max-width:760px}
.cap-head h2{font-size:clamp(30px,2.4vw+14px,48px);letter-spacing:-.01em;margin-top:2px}

.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:44px}
.fc{background:var(--branco);border:1px solid var(--linha);border-radius:20px;padding:26px 24px;break-inside:avoid}
.cap.nevoa .fc{background:#fff;border-color:rgba(0,0,0,.06)}
.fc-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--sec);margin-bottom:16px}
.fc h3{font-size:20px;letter-spacing:-.01em}
.fc p{margin-top:8px;color:var(--tinta-2);font-size:16px;line-height:1.5}
.tg{display:inline-block;margin-left:8px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--sec);background:var(--soft);padding:3px 8px;border-radius:980px;vertical-align:middle}

/* storyboard */
.board{margin:48px 0 0;padding:30px;border-radius:24px;background:var(--soft);break-inside:avoid}
.board-cap{margin-bottom:22px}
.board-cap b{display:block;font-size:22px;font-weight:600;letter-spacing:-.01em}
.board-strip{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.bp{flex:1 1 180px;background:#fff;border-radius:16px;padding:20px 18px;position:relative;break-inside:avoid}
.bp-n{position:absolute;top:14px;right:16px;font-size:12px;font-weight:700;color:var(--sec)}
.bp-art{display:block;color:var(--sec)}
.scene{width:56px;height:44px}
.bp b{display:block;margin-top:12px;font-size:17px;font-weight:600;letter-spacing:-.01em}
.bp i{display:block;margin-top:6px;font-style:normal;font-size:14.5px;line-height:1.45;color:var(--tinta-2)}
.bp-arr{display:flex;align-items:center;color:var(--sec);font-size:20px;opacity:.55}
@media(max-width:860px){.bp-arr{display:none}}

/* media row */
.mrow{display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center;margin-top:48px}
.mrow.flip .m-media{order:2}
@media(max-width:860px){.mrow{grid-template-columns:1fr}.mrow.flip .m-media{order:0}}
.m-copy h3{font-size:26px;letter-spacing:-.012em}
.m-copy p{margin-top:12px;color:var(--tinta-2);font-size:17px;line-height:1.5}
.shot img{width:100%;border-radius:20px}

/* checklist */
.check{margin-top:36px;display:grid;gap:14px}
.check li{display:flex;gap:12px;align-items:flex-start;font-size:17px;line-height:1.45;break-inside:avoid}
.ck{flex:0 0 auto;width:20px;height:20px;margin-top:2px;border-radius:50%;background:var(--terra-leve);position:relative}
.ck::after{content:"";position:absolute;left:6px;top:5px;width:5px;height:9px;border:2px solid var(--terra-esc);
  border-top:0;border-left:0;transform:rotate(42deg)}

/* setores */
.setores{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:44px}
@media(max-width:860px){.setores{grid-template-columns:repeat(2,1fr)}}
.setor{break-inside:avoid}
.setor img{width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:18px}
.setor b{display:block;margin-top:12px;font-size:18px;font-weight:600;letter-spacing:-.01em}
.setor span{display:block;margin-top:4px;font-size:14.5px;line-height:1.45;color:var(--tinta-2)}

/* preço */
.planos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:44px}
@media(max-width:860px){.planos{grid-template-columns:1fr}}
.plano{border:1px solid var(--linha);border-radius:24px;padding:30px 26px;background:#fff;break-inside:avoid}
.plano .nome{font-size:13px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--tinta-2)}
.plano .v{margin-top:14px;font-size:46px;font-weight:600;letter-spacing:-.03em;line-height:1}
.plano .u{margin-top:6px;font-size:14px;color:var(--tinta-2)}
.plano p{margin-top:14px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}
.plano.hi{background:var(--preto);border-color:var(--preto);color:var(--claro)}
.plano.hi .nome{color:var(--terra-vivo)}
.plano.hi .v{color:#fff}
.plano.hi .u,.plano.hi p{color:var(--claro-2)}
.naos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:20px}
@media(max-width:860px){.naos{grid-template-columns:1fr}}
.nao{border-radius:20px;padding:24px;background:#fff;border:1px solid var(--linha);break-inside:avoid}
.nao h4{margin:0;font-size:18px;font-weight:600;letter-spacing:-.01em}
.nao p{margin-top:8px;font-size:15.5px;line-height:1.5;color:var(--tinta-2)}

/* lineup */
.lineup{background:var(--preto);color:var(--claro);padding:clamp(80px,10vw,130px) 0}
.lineup-in{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.lineup h2{font-size:clamp(30px,2.4vw+14px,48px);color:#fff}
.lineup .lead{color:var(--claro-2)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:44px}
.tile{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:24px;break-inside:avoid}
.tile h3{font-size:18px;color:#fff}
.tile p{margin-top:8px;font-size:15px;line-height:1.5;color:var(--claro-2)}
.tile-mk{display:block;width:26px;height:3px;border-radius:3px;background:var(--sec);margin-bottom:14px}

/* cta / download / rodapé */
.cta{text-align:center;padding:clamp(88px,11vw,140px) 24px;background:
  radial-gradient(1100px 560px at 50% 0%,rgba(124,58,237,.5),transparent 65%),#0b0a0e;color:var(--claro)}
.cta h2{font-size:clamp(30px,3vw+12px,52px);color:#fff;max-width:18ch;margin:0 auto}
.cta p{margin:20px auto 0;max-width:52ch;font-size:19px;line-height:1.5;color:var(--claro-2)}
.dl{text-align:center;padding:clamp(64px,8vw,96px) 24px;background:var(--nevoa)}
.dl h2{font-size:30px}
.dl p{margin-top:12px;color:var(--tinta-2)}
.foot{border-top:1px solid var(--linha);padding:36px 24px;background:var(--nevoa)}
.foot-in{max-width:var(--maxw);margin:0 auto;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;
  color:var(--tinta-2);font-size:13px}

/* reveal */
.rev{opacity:0;transform:translateY(30px);transition:opacity .9s var(--ease),transform .9s var(--ease)}
.rev.vis{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.rev{opacity:1;transform:none}html{scroll-behavior:auto}}

/* ======================= IMPRESSÃO / PDF =======================
   As três travas do playbook. Mexer aqui quebra o PDF em silêncio. */
@media print{
  /* 1. sem isto o PDF sai EM BRANCO (o reveal nunca dispara sem scroll) */
  .rev{opacity:1!important;transform:none!important}
  /* 2. sem isto hero/CTA/fotos saem sem cor */
  *{-webkit-print-color-adjust:exact!important;print-color-adjust:exact!important}
  /* 3. só nas unidades atômicas — NUNCA por capítulo (gera página quase vazia) */
  .fc,.bp,.plano,.nao,.tile,.setor,.board,.check li{break-inside:avoid}
  .nav,.dl,.btns{display:none!important}
  .cap{padding:28px 0}
  .hero{padding-top:36px}
  .credo{padding:44px 24px}
  body{font-size:11.5pt}
  a{color:inherit;text-decoration:none}
  /* sem isto o Chrome imprime em Letter (padrão americano) — no Brasil é A4 */
  @page{size:A4;margin:14mm}
}
"""

SCRIPT = """<script>
(function(){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches){
    document.querySelectorAll(".rev").forEach(function(e){e.classList.add("vis")});return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add("vis");io.unobserve(e.target)}})},
    {threshold:0,rootMargin:"0px 0px -12% 0px"});
  document.querySelectorAll(".rev").forEach(function(e){io.observe(e)});
})();
</script>"""

# --------------------------------------------------------------------- montagem
def build():
    _CHAP[0] = 0
    wa_svg = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="width:18px;height:18px">'
              '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.6 0-3.1-.4-4.4-1.2'
              'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Z"/></svg>')

    nav = f'''<nav class="nav">
  <a class="brand" href="/"><img src="/assets/brand-mark.png" width="24" height="24" alt="">
    <span>acompanhaobra<span class="tld">.app</span></span></a>
  <span class="nav-r"><span class="nav-links">
    <a href="#obra">Do condomínio</a><a href="#unidade">Da unidade</a>
    <a href="#preco">Preço</a><a href="#limites">O que não faz</a></span>
  <a class="nav-cta" href="{WA}">Falar no WhatsApp</a></span>
</nav>'''

    hero = f'''<header class="hero">
  <span class="eyebrow">{C.HERO["eyebrow"]}</span>
  <h1>{C.HERO["h1"]}</h1>
  <p class="sub">{C.HERO["sub"]}</p>
  <div class="btns"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
  <div class="hero-stage rev"><img src="/assets/hero.jpg" width="1600" height="1067"
    alt="Operários em andaime na reforma da fachada de um prédio, com o síndico observando do chão."></div>
</header>'''

    credo = f'<section class="credo rev"><h2>{C.CREDO}</h2></section>'

    cap_obra = chapter("obra", "Obra do condomínio", "Você contrata; o sistema cobra o prazo.",
        "Fachada, telhado, elevador, garagem. As etapas têm data, a medição vira parcela e o aditivo "
        "é assinado antes de virar conta.",
        board("obra"), cards(C.OBRA, "terra"))

    cap_unidade = chapter("unidade", "Reforma de unidade", "A norma põe a reforma do vizinho no seu colo.",
        "A NBR 16280 responsabiliza o condomínio pela obra que acontece dentro do apartamento. Aqui "
        "ela chega com projeto, ART e termo — não por mensagem no grupo.",
        mrow(foto("bento-art", "Prancheta com a planta da reforma sobre a bancada da obra."),
             "A ART deixa de ser um PDF que ninguém lê.",
             "Do documento saem o engenheiro, o CREA ou CAU, o número da ART, a área e se há "
             "intervenção estrutural. O síndico confere o que a norma pede em vez de digitar.", True),
        board("nbr"),
        cards(C.UNIDADE, "petroleo"))

    cap_fiscal = chapter("fiscalizacao", "Fiscalização", "Quem não regulariza, responde.",
        "Areia na rua, caçamba fora de hora, obra no domingo. O registro sai com foto e prazo — e o "
        "morador não alega que ninguém avisou.",
        board("fiscal"),
        cards(C.FISCAL, "ambar"))

    cap_equipe = chapter("equipe", "A equipe da obra", "O engenheiro entra, e só na obra dele.",
        "Quem toca a obra precisa subir documento e foto sem passar pelo WhatsApp do síndico — e sem "
        "enxergar o resto do condomínio.",
        mrow(foto("bento-equipe", "Engenheira de capacete e colete conversa com o síndico no hall do prédio."),
             "Convite por e-mail, acesso que expira.",
             "Ele clica e cai direto na obra. Não vê o financeiro, não vê os moradores, não vê as "
             "outras obras. Concluída a obra, o acesso se encerra sozinho."),
        cards(C.EQUIPE, "petroleo"))

    cap_dinheiro = chapter("dinheiro", "O dinheiro", "O síndico não vira contador para pagar a obra.",
        "A medição do mês é uma parcela. A retenção entra sozinha, e a declaração à Receita sai junto "
        "com as outras do mês.",
        cards(C.DINHEIRO, "terra"))

    cap_painel = chapter("painel", "No comando", "Dá para ver o atraso nascendo.",
        "O previsto e o realizado no mesmo lugar, mês a mês — em vez de descobrir no fim que a obra "
        "derrapou.",
        cards(C.PAINEL, "ambar"))

    setores = "".join(
        f'<figure class="setor rev"><img src="/assets/{s}.jpg" alt="{r}" loading="lazy" decoding="async">'
        f'<b>{r}</b><span>{d}</span></figure>' for s, r, d in C.SETORES)
    cap_quem = chapter("quem", "Para quem é", "Se o prédio tem obra, serve.",
        "Síndico morador ou profissional, administradora e gestor de loteamento — do retrofit de "
        "fachada à reforma de um apartamento só.",
        f'<div class="setores">{setores}</div>',
        '<div class="cap-head rev" style="margin-top:64px"><h2 style="font-size:30px">'
        'O que dói hoje.</h2></div>',
        lista(C.DORES))

    planos = "".join(
        f'<div class="plano{" hi" if i == 1 else ""}"><div class="nome">{n}</div>'
        f'<div class="v">{v}</div><div class="u">{u}</div><p>{d}</p></div>'
        for i, (n, v, u, d) in enumerate(C.PRECO))
    naos = "".join(f'<div class="nao"><h4>{t}</h4><p>{d}</p></div>' for t, d in C.NAOS)
    cap_preco = chapter("preco", "Preço", "R$ 79 por mês, por condomínio.",
        "A primeira obra é grátis, do cadastro ao termo de conclusão. Sem taxa de implantação, sem "
        "cobrança por obra aberta e sem fidelidade.",
        f'<div class="planos rev">{planos}</div>',
        f'<div class="naos rev">{naos}</div>')

    cap_limites = chapter("limites", "Honestidade", "O que o acompanhaobra não faz.",
        "Um livreto que só lista virtude não ajuda ninguém a decidir. Isto aqui é o que ele "
        "<b>não</b> resolve — para você não descobrir depois de assinar.",
        cards(C.NAO_FAZ, "ambar"))

    cap_lei = chapter("lei", "A norma", "O papel que responde por você depois.",
        "Quando alguém perguntar por que a obra foi autorizada, a resposta precisa estar assinada — "
        "não na memória de quem era síndico na época.",
        cards(C.COMPLIANCE, "petroleo"))

    tiles = "".join(f'<article class="tile c-{c}"><span class="tile-mk"></span>'
                    f'<h3>{n}{tag(g)}</h3><p>{d}</p></article>' for n, d, c, g in C.TILES)
    lineup = f'''<section class="lineup" id="modulos">
  <div class="lineup-in">
    <h2 class="rev">Tudo o que ele faz.</h2>
    <p class="lead rev">Nada aqui é opcional pago: a empresa liga o que a operação dela precisa.</p>
    <div class="tiles rev">{tiles}</div>
  </div>
</section>'''

    h2, p = C.CTA
    cta = f'''<section class="cta">
  <h2 class="rev">{h2}</h2>
  <p class="rev">{p}</p>
  <div class="btns rev"><a class="btn btn-branco" href="{WA}">{wa_svg} Falar no WhatsApp</a></div>
</section>'''

    dl = '''<section class="dl">
  <h2>Leve o livreto com você.</h2>
  <p>Baixe o PDF para apresentar offline ou mandar por e-mail.</p>
  <div class="btns"><a class="btn" href="/livreto.pdf" download="livreto-acompanhaobra.pdf">
    Baixar o livreto (PDF)</a></div>
</section>'''

    body = "\n".join([nav, hero, credo, cap_obra, cap_unidade, cap_fiscal, cap_equipe,
                      cap_dinheiro, cap_painel, cap_quem, cap_preco, cap_limites, cap_lei,
                      lineup, cta, dl])

    hoje = datetime.date.today().strftime("%d/%m/%Y")
    sha = hashlib.sha1(body.encode()).hexdigest()[:7]
    foot = (f'<footer class="foot"><div class="foot-in">'
            f'<span>acompanhaobra · controle de obra de condomínio · '
            f'<a href="{C.SITE}/privacidade">Privacidade</a></span>'
            f'<span>Livreto v{hoje} · {sha}</span></div></footer>')

    desc = ("Livreto do acompanhaobra: controle da obra do condomínio e da reforma de unidade pela "
            "NBR 16280. Cotação por link, contrato e aditivo assinados, etapas com prazo, medição "
            "com INSS retido e EFD-Reinf, fiscalização e painel. R$ 79 por mês, a primeira obra é grátis.")
    url = f"{C.SITE}/livreto/"
    head = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Livreto do acompanhaobra — controle de obra do contrato ao termo de conclusão</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="acompanhaobra">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{url}">
<meta property="og:title" content="Livreto do acompanhaobra">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{C.SITE}/assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600&display=swap" rel="stylesheet">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SoftwareApplication",
"name":"acompanhaobra","applicationCategory":"BusinessApplication","operatingSystem":"Web",
"url":"{url}","inLanguage":"pt-BR","description":"{desc}",
"offers":{{"@type":"Offer","price":"79","priceCurrency":"BRL"}},
"featureList":["Cotação por link que o fornecedor responde sem criar login",
"Contrato, projeto e ART anexados à obra com assinatura digital",
"Etapas com data prevista e percentual executado",
"Aditivo assinado e aplicado na parcela seguinte",
"Reforma de unidade pela NBR 16280 com ART lida por IA",
"Fiscalização com foto e prazo que escala para infração",
"Medição com retenção de INSS e EFD-Reinf",
"Equipe externa com acesso restrito à obra",
"Painel da obra, relatório em PDF e carteira da administradora"]}}</script>
<style>{CSS}</style>
</head>
<body>
'''
    doc = head + body + "\n" + foot + "\n" + SCRIPT + "\n</body>\n</html>\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(doc)
    print(f"[livreto] {OUT} — {len(doc)//1024} KB · v{hoje} · {sha}")

build()
