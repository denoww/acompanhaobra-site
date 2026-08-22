#!/usr/bin/env python3
"""Gera o sitemap e trava os invariantes de SEO das páginas estáticas.

Roda no CI (.github/workflows/seo.yml) e também na mão:

    python3 .github/scripts/seo.py            # gera + confere (sem rede)
    python3 .github/scripts/seo.py --check    # só confere, não escreve
    python3 .github/scripts/seo.py --http     # confere também se cada <loc> é 200 sem redirect

⚠️ Vive em `.github/` de propósito: o GitHub Pages não publica esse diretório.
Um script de build em `tools/` ou na raiz seria SERVIDO — foi exatamente o
vazamento que o `_config.yml` teve que tapar (o `/livreto/content.py` estava no
ar, com os caminhos internos do foundry dentro).

⚠️ Nada aqui vai para `assets/`: o fingerprint do `livreto.yml` é
`find livreto/index.html assets -type f`, então qualquer arquivo novo lá dispara
regeneração de 1,5-2,7 MB de PDF e um commit do bot a cada push.

## A decisão que mata uma classe inteira de bug

O `<loc>` de cada página é o **próprio canonical dela**, lido do HTML. Não existe
"mapa de página → URL" para alguém deixar desatualizado, e o clássico
`canonical=/livreto/` com `<loc>=/livreto` (que fez o Google escolher a URL que
redireciona) deixa de ser possível por construção — não por checagem.

Página com `noindex` fica fora do sitemap. É o mesmo sinal, num lugar só.
"""
from __future__ import annotations

import html as H
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Sitemap do blog, servido pelo Rails do ERP. Entra no índice porque a
# propriedade do Search Console é de DOMÍNIO (cobre www, apex e blog.), o que
# torna o cross-submit legítimo.
# ⚠️ SEM `.xml`. A rota do Rails é `/sitemap` (config/routes/blog.rb); `/sitemap.xml`
# responde **301** para ela. Sitemap entregue ao Google por redirect vira aviso no
# Search Console — e este mesmo script reprova `<loc>` que não devolve 200 direto,
# então o `.xml` era incoerente com a própria regra. Achado em 21/08/2026, ao conferir
# o índice recém-submetido; as 3 marcas herdaram o `.xml` do mesmo blueprint.
SITEMAP_BLOG = 'https://blog.acompanhaobra.app/sitemap'
BASE = 'https://www.acompanhaobra.app'

# Copy que não pode existir em página pública. Mesma doutrina do guard do blog:
# a frase honesta NEGA a promessa, então "não existe integração com folha" tem
# que passar — daí o detector de negação logo antes do trecho.
PROIBIDAS = [
    # ⚠️ O regex exige uma construção de VANGLÓRIA antes do número ("mais de",
    # "já são", "atendemos", "+"). Sem isso ele acusava a descrição do ICP na
    # home — "Empresa de 5 a 100 funcionários com gente em turno" —, que é
    # justamente a copy certa. Guard que reprova texto honesto vira guard que
    # todo mundo aprende a ignorar.
    ('prova social inventada',
     r'(mais\s+de|j[áa]\s+s[ãa]o|atendemos|usado\s+por|confiam|\+\s*)\s*\d[\d.]*\s*(mil\s+)?'
     r'(empresas|clientes|usu[áa]rios|funcion[áa]rios|batidas)\b'),
    ('métrica de acurácia ou disponibilidade',
     r'\d{2}[,.]?\d*\s*%\s*(de\s*)?(acerto|precis[ãa]o|uptime|disponibilidade)|99[,.]9'),
    # ⚠️ `\b` obrigatório em todo nome curto: sem ele um pedaço casa dentro de outra
    # palavra e o guard reprova copy legítima. Já aconteceu duas vezes na casa —
    # `ucondo` casando em "se|ucondo|mínio", e `rdo` casando em "aco|rdo|".
    ('concorrente pelo nome',
     r'\b(sienge|vobi|obra\s*prima|mobuss|vigha|or[çc]afascio|construct\s*app)\b'),
    # ── As 5 abaixo são as promessas de OBRAS que o ERP não sustenta. Fonte única:
    # `livreto/CLAUDE.md` seção Obras + os checkboxes abertos em
    # `app/services/obras/ROADMAP.md` (L7b, L24c/L25, L10b, L17, L27), reconferidos
    # em 2026-08-19. Escritas ANTES da copy de propósito: guard que nasce depois do
    # texto nasce escrevendo exceção pro texto que já está lá.
    ('RDO ou diário de obra por WhatsApp/áudio',
     r'\brdo\b[^.\n]{0,80}(whatsapp|[áa]udio)|(whatsapp|[áa]udio)[^.\n]{0,80}\brdo\b'
     r'|di[áa]rio de obra[^.\n]{0,80}(whatsapp|[áa]udio)|(whatsapp|[áa]udio)[^.\n]{0,80}di[áa]rio de obra'),
    ('app de campo ou PWA do mestre de obras',
     r'(app|aplicativo|pwa)[^.\n]{0,40}(de campo|do mestre de obras|do empreiteiro)'),
    # ⚠️ O `(?!\bn[ãa]o\b)` no meio NÃO é decoração. O escape por NEGADORES só olha o que
    # vem ANTES do match, e aqui o match começa em "cotação" — então a copy correta do
    # capítulo de honestidade ("A cotação NÃO dispara o e-mail") tinha o negador DENTRO
    # do trecho casado e era reprovada. Guard que reprova o texto honesto é guard que
    # todo mundo aprende a ignorar.
    ('cotação que ENVIA e-mail ao fornecedor',
     r'(cota[çc][ãa]o|or[çc]amento)((?!\bn[ãa]o\b)[^.\n]){0,60}(sistema envia|envia o e-?mail|envia e-?mail|dispara o e-?mail)'),
    # LADO ÚNICO: a retenção de INSS e a geração/transmissão do R-2010 são REAIS e
    # podem ser ditas. O que não existe é o status fiscal filtrado POR OBRA na tela.
    ('status de EFD-Reinf por obra',
     r'(efd-?reinf|r-?2010)[^.\n]{0,40}por obra|por obra[^.\n]{0,40}(efd-?reinf|r-?2010)'),
    ('retenção contratual ou caução de garantia',
     r'reten[çc][ãa]o contratual|cau[çc][ãa]o[^.\n]{0,40}(obra|empreiteiro)'),
    ('certificação não confirmada',
     r'INPI|homologad\w+\s+(pelo|junto)|certificad\w+\s+pelo\s+(MTE|Minist[ée]rio)'),
    ('garantia absoluta',
     r'garantimos que|100%\s*(seguro|garantido|livre)|nunca\s+falha|zero\s+risco'),
    ('marcador de rascunho',
     r'\[A VALIDAR|\[INSERIR|\[TODO|R\$\s*_+|XXX+|lorem ipsum'),
]
NEGADORES = re.compile(r'\b(n[ãa]o|ningu[ée]m|nunca|nenhum[ao]?|jamais|sem)\b[^.\n]{0,60}$', re.I)

erros: list[str] = []


def falha(msg: str) -> None:
    erros.append(msg)
    print(f'::error::{msg}')


def excluidas_do_jekyll() -> list[str]:
    """Prefixos que o `_config.yml` manda o Jekyll NÃO publicar.

    Lido do arquivo em vez de repetido aqui: o `tools/mockup/phone.html` é
    rastreado pelo git mas responde 404 em produção (conferido). Manter uma
    segunda lista significaria, no dia em que alguém excluir uma pasta nova, um
    guard cobrando canonical de página que não existe no ar.
    """
    cfg = RAIZ / '_config.yml'
    if not cfg.exists():
        return []
    dentro, itens = False, []
    for linha in cfg.read_text(encoding='utf-8').splitlines():
        if re.match(r'^exclude:\s*$', linha):
            dentro = True
            continue
        if dentro:
            m = re.match(r'^\s*-\s*"?([^"#]+?)"?\s*(#.*)?$', linha)
            if m:
                itens.append(m.group(1).strip().rstrip('/'))
            elif linha.strip() and not linha.startswith((' ', '\t', '-')):
                break
    return itens


def paginas() -> list[Path]:
    saida = subprocess.run(['git', 'ls-files', '*.html'], cwd=RAIZ,
                           capture_output=True, text=True, check=True).stdout
    fora = excluidas_do_jekyll()
    return [RAIZ / p for p in saida.split()
            if p and not any(p == x or p.startswith(x + '/') for x in fora)]


def texto_visivel(bruto: str) -> str:
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', bruto, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s))


def lastmod(caminho: Path) -> str:
    """Data do último commit que tocou o arquivo.

    `git log`, não mtime: mtime é a data do CHECKOUT no runner (hoje, sempre), o
    que faria todo lastmod mentir "atualizado agora" a cada push.
    """
    r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', str(caminho.relative_to(RAIZ))],
                       cwd=RAIZ, capture_output=True, text=True)
    return r.stdout.strip() or '1970-01-01'


def confere_faq(arq: Path, bruto: str, visivel: str) -> None:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', bruto, re.S)
    if not m:
        return
    try:
        grafo = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        falha(f'{arq.name}: JSON-LD inválido ({e})')
        return

    nos = grafo.get('@graph', [grafo])
    bruto_json = m.group(1)
    # ⚠️ Checar no JSON, NÃO no texto do arquivo: o comentário HTML que explica a
    # proibição contém a própria palavra e daria falso positivo eterno.
    for proibido in ('aggregateRating', '"review"', 'interactionStatistic'):
        if proibido in bruto_json:
            falha(f'{arq.name}: {proibido} em dado estruturado — prova social fabricada')

    for no in nos:
        if no.get('@type') != 'FAQPage':
            continue
        for q in no.get('mainEntity', []):
            for rotulo, txt in (('pergunta', q.get('name', '')),
                                ('resposta', q.get('acceptedAnswer', {}).get('text', ''))):
                if re.sub(r'\s+', ' ', txt).strip() not in visivel:
                    falha(f'{arq.name}: {rotulo} do FAQPage não existe no texto visível: '
                          f'"{txt[:60]}…"')


def confere_assets(arq: Path, bruto: str) -> None:
    """Todo `/assets/...` referenciado tem que existir em disco.

    ⚠️ Referenciar imagem que não existe NÃO quebra nada visível: o navegador só não
    mostra o ícone, e o PDF sai com um retângulo vazio. `bento-art.jpg` e
    `bento-equipe.jpg` foram para produção assim, dentro do PDF do livreto, e só foram
    descobertas por leitura humana. O guard de página-em-branco não pega, porque a
    página tem texto.

    Cobre `src=` e `href=` (favicon, apple-touch-icon, preload) e o `srcset`.
    """
    # `/assets/...` é sempre absoluto a partir da raiz do site — inclusive dentro de
    # /livreto/, que referencia por caminho absoluto. Daí usar RAIZ e não arq.parent.

    vistos = set()
    for m in re.finditer(r'(?:src|href)="(/assets/[^"?#]+)"', bruto):
        vistos.add(m.group(1))
    for m in re.finditer(r'srcset="([^"]+)"', bruto):
        for parte in m.group(1).split(','):
            cand = parte.strip().split(' ')[0]
            if cand.startswith('/assets/'):
                vistos.add(cand)

    for ref in sorted(vistos):
        if not (RAIZ / ref.lstrip('/')).is_file():
            falha(f'{arq.name}: referencia {ref}, que NÃO existe em disco')


def confere_copy(arq: Path, visivel: str) -> None:
    for nome, padrao in PROIBIDAS:
        for m in re.finditer(padrao, visivel, re.I):
            antes = visivel[max(0, m.start() - 80):m.start()]
            if NEGADORES.search(antes):
                continue  # a frase está NEGANDO a promessa — é a copy certa
            trecho = visivel[max(0, m.start() - 50):m.end() + 50].strip()
            falha(f'{arq.name}: copy proibida ({nome}): "…{trecho}…"')
            break


def confere_http(urls: list[str]) -> None:
    """Cada <loc> tem que responder 200 SEM redirect.

    Redirect no sitemap é o bug do `/livreto` (canonical sem barra, URL com):
    o Google segue o salto, escolhe a URL final e o `<loc>` vira desperdício de
    crawl. `<loc>` que aponta pra 301 é sempre erro de mapeamento.

    ⚠️ URL NOVA vira aviso, não erro. Este workflow roda no push; a página só
    existe no ar depois que o Pages publica, alguns segundos ou minutos depois.
    Falhar aqui reprovaria justamente o commit que ADICIONA uma página — e o
    autor aprenderia a ignorar o job. Compara com o sitemap do commit anterior
    pra saber quem é novo.
    """
    import urllib.error
    import urllib.request

    anterior = subprocess.run(['git', 'show', 'HEAD:sitemap.xml'], cwd=RAIZ,
                              capture_output=True, text=True)
    ja_existiam = set(re.findall(r'<loc>([^<]+)</loc>', anterior.stdout))

    for u in urls:
        req = urllib.request.Request(u, method='HEAD',
                                     headers={'User-Agent': 'seo.py/1.0 (CI)'})
        classe = urllib.request.HTTPRedirectHandler

        class SemRedirect(classe):
            def redirect_request(self, *a, **k):
                return None

        opener = urllib.request.build_opener(SemRedirect)
        try:
            with opener.open(req, timeout=20) as r:
                if r.status != 200:
                    raise urllib.error.HTTPError(u, r.status, 'status', r.headers, None)
        except Exception as e:
            codigo = getattr(e, 'code', type(e).__name__)
            if u in ja_existiam:
                falha(f'<loc> {u} respondeu {codigo} — sitemap não pode listar redirect nem erro')
            else:
                print(f'::warning::<loc> {u} respondeu {codigo}, mas é URL NOVA — '
                      f'o Pages pode não ter publicado ainda')


def main() -> int:
    so_confere = '--check' in sys.argv
    urls: list[tuple[str, str]] = []

    for arq in sorted(paginas()):
        bruto = arq.read_text(encoding='utf-8')
        visivel = texto_visivel(bruto)

        confere_copy(arq, visivel)
        confere_faq(arq, bruto, visivel)
        confere_assets(arq, bruto)

        if re.search(r'name="robots"[^>]*content="[^"]*noindex', bruto):
            continue  # 404, /entrar e afins ficam fora do sitemap, por decisão da própria página

        if not re.search(r'name="description"', bruto):
            falha(f'{arq.name}: página indexável sem meta description')
        n_h1 = len(re.findall(r'<h1[\s>]', bruto))
        if n_h1 != 1:
            falha(f'{arq.name}: {n_h1} <h1> (tem que ser exatamente 1)')

        mc = re.search(r'rel="canonical"\s+href="([^"]+)"', bruto)
        if not mc:
            falha(f'{arq.name}: página indexável sem canonical — não entra no sitemap')
            continue
        urls.append((mc.group(1), lastmod(arq)))

    if len(urls) != len({u for u, _ in urls}):
        falha('duas páginas declaram o MESMO canonical')

    if not so_confere and not erros:
        gravar(urls)

    if '--http' in sys.argv and not erros:
        confere_http([u for u, _ in urls])

    print(f'{len(urls)} URLs, {len(erros)} erro(s)')
    return 1 if erros else 0


def gravar(urls: list[tuple[str, str]]) -> None:
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in sorted(urls):
        linhas += ['  <url>', f'    <loc>{loc}</loc>', f'    <lastmod>{mod}</lastmod>', '  </url>']
    linhas.append('</urlset>')
    (RAIZ / 'sitemap.xml').write_text('\n'.join(linhas) + '\n', encoding='utf-8')

    idx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for s in (f'{BASE}/sitemap.xml', SITEMAP_BLOG):
        idx += ['  <sitemap>', f'    <loc>{s}</loc>', '  </sitemap>']
    idx.append('</sitemapindex>')
    (RAIZ / 'sitemap-index.xml').write_text('\n'.join(idx) + '\n', encoding='utf-8')


if __name__ == '__main__':
    sys.exit(main())
