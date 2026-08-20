# Livreto do acompanhaobra — playbook

Peça funda de vendas, servida em `/livreto/` com PDF espelho em `/livreto.pdf`.

## A regra de ouro

> **Edite `content.py` e dê push. NÃO rode `build.py` na mão.**

O CI (`.github/workflows/livreto.yml`) regenera o HTML, gera o PDF por Chromium headless,
**abre o PDF e mede** se alguma página saiu em branco, e commita o espelho de volta. Rodar o
build localmente não é errado — o CI só confirma que já estava em dia —, mas **editar
`livreto/index.html` à mão é**: é arquivo gerado, e o próximo push o sobrescreve.

⚠️ **`git diff --quiet` não enxerga arquivo untracked.** Foi assim que, no primeiro run
deste repo, o PDF foi gerado, passou no guard de página em branco e mesmo assim não foi
commitado — o job ficou verde e `/livreto.pdf` respondia 404. O passo de commit usa
`git status --porcelain`. Se for portar este workflow para outro repo novo, leve a correção.

## Onde editar

| Quero mudar | Arquivo |
|---|---|
| Texto dos cards, storyboards, preço, "o que não faz" | `content.py` — 95% das mudanças |
| Quais capítulos entram, hero, CTA, SEO, nav | `build.py` → o dict do profile e `build()` |
| Cenas dos storyboards (SVG line-art) | `build.py` → `SCENES` |
| Cores e CSS de tela e de impressão | `build.py` → `CSS` |

## As 4 travas do `@media print` (quebram em silêncio)

1. **`.rev{opacity:1}`** — sem isto o PDF sai **EM BRANCO**: o reveal por scroll nunca
   dispara na impressão. É a falha nº 1 desta família de livretos.
2. **`print-color-adjust:exact`** — sem isto hero, CTA e fotos saem sem cor.
3. **`break-inside:avoid` só nas unidades atômicas** (card, painel). Nunca por capítulo —
   gera páginas quase vazias.
4. **`@page{size:A4}`** — sem isto o Chrome imprime em Letter.

## Antes de adicionar uma foto

`foto("x")` gera `<img src="/assets/x.jpg">` sem validar nada. Se o arquivo não existir, a
página publicada e o PDF ficam com imagem quebrada e **nenhum workflow reclama** (o guard de
página em branco só mede se a página tem tinta, e texto conta). Confira `assets/x.jpg`.

## Conteúdo: só o que roda

As listas de cards são um recorte do `/livreto/obras` do ERP, e a fonte da verdade do que
pode ser dito é `app/services/obras/ROADMAP.md` no repo `denoww/seucondominio`. O cabeçalho
do `content.py` traz os 10 ⛔ com o lote correspondente; o capítulo `NAO_FAZ` existe
justamente para dizê-los em voz alta. Um livreto que só lista virtude não ajuda ninguém a
decidir — e o guard `seo.py` reprova o push que prometer qualquer um deles.
