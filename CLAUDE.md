# acompanhaobra-site — playbook

Site institucional do **acompanhaobra** (controle de obra de condomínio e reforma de
unidade pela NBR 16280). Estático, sem build de framework. Servido por **GitHub Pages** em
`https://www.acompanhaobra.app`.

Diferente das duas irmãs (`baterponto`, `atendeaqui`), este **não** é um produto "fora do
nicho condomínio": é o **módulo de Obras do ERP SeuCondomínio** vendido com marca própria,
para o mesmo síndico. Isso muda uma coisa prática — a fonte da verdade do que pode ser
prometido é `app/services/obras/ROADMAP.md` **no repo do ERP** (`denoww/seucondominio`),
não um pack de posicionamento. Nada entra na copy sem estar entregue lá.

## Deploy

> **Deploy = `git push`.** Não existe passo separado.

GitHub Pages publica o `main` direto (~40–60s + CDN). Para conferir que produção já serve o
seu commit — não confie no "subiu":

```bash
diff <(curl -s https://www.acompanhaobra.app/index.html) index.html && echo "prod == HEAD"
```

**Domínio:** o `CNAME` do repo é `www.acompanhaobra.app` (host canônico); o apex faz 301 →
www. ⚠️ **`.app` é um TLD com HSTS preload**: sem certificado o navegador recusa a conexão,
sem opção de prosseguir — `curl` por HTTP responder 200 **não** significa "no ar".

⚠️ **Pages em `errored` não provisiona certificado.** Em 20/08/2026 vários pushes seguidos
geraram deploys concorrentes, um falhou, e o site ficou horas em `"status": "errored"` — com
o certificado parado, sem nenhum aviso. Diagnóstico: `gh api repos/denoww/acompanhaobra-site/pages`.
O conserto é fazer um push que reconstrua; o relógio do certificado só começa a correr
quando o status volta a `built`.

## Estrutura

| O quê | Onde |
|---|---|
| Landing (CSS + HTML + JS num arquivo) | `index.html` |
| Livreto de vendas (gerado) | `livreto/` → `content.py` é 95% das mudanças |
| Política de privacidade | `privacidade.html` |
| Fotos (JPEG otimizado) | `assets/` |
| Emissão do cert ACM do blog | `tools/cert-acm-cloudshell.sh` |

**Fonte única de contato e login:** os dotfiles `.whatsapp` e `.login` na raiz. Dotfile não
é publicado pelo Pages, e o `guarda.yml` reprova o push se algum `wa.me` do HTML divergir.
Trocou de número? Edite `.whatsapp` e mais nada.

## Design — padrão Apple

Herdado do `baterponto-site` (que tirou os números do CSS de produção da apple.com):

- **Tipografia**: tracking **não-monotônico** — `-.015em` em 80px, ~zero em 40px,
  **positivo** (`+.011em`) em 21px, `-.022em` em 17px. Peso de título **600**, nunca 700.
- **Superfícies**: branco ↔ `#f5f5f7` ↔ preto, alternando. **Sem borda entre seções** — o
  divisor é o contraste de fundo.
- **Cards**: radius 28px e **`box-shadow: none`**.
- **Botões**: pill `border-radius: 980px`, padding 12/22, peso 400.
- **Movimento**: `opacity 0→1` + `translateY(30px)→0`, **900ms**, `cubic-bezier(.45,0,.55,1)`,
  stagger 150ms, dispara **uma vez** (IntersectionObserver + `unobserve`).
- **Cor da marca**: âmbar `#B45309` (`--terra`), com `#92400E` para hover e para **texto
  pequeno** — em 11px o `#B45309` fica em ~4,1:1, abaixo do AA.

**Sem Google Fonts de propósito.** A stack começa em `-apple-system`/`BlinkMacSystemFont`,
que resolvem para a fonte do sistema antes de chegar em qualquer webfont fora de Apple: era
CSS de terceiro no caminho crítico por quase nada, e entregava o IP do visitante a um
terceiro que a política de privacidade teria de declarar.

## A regra que manda em tudo: só o que roda

⛔ **NUNCA prometer** (verificado em 19/08/2026 contra o ROADMAP do módulo; todos com o
checkbox ainda aberto lá): RDO/diário por WhatsApp com áudio transcrito (L7b) · app ou PWA
de campo para o mestre (L24c/L25) · cotação que **envia** e-mail ao fornecedor (L10b — o
sistema **gera o link**, o síndico manda) · status de EFD-Reinf **por obra** (L17 — a
retenção de INSS e a transmissão do R-2010 **são reais**; o filtro por obra é que não
existe) · retenção contratual de 5–10% (L27) · liberar garantia (L31) · obra→patrimônio
(L32) · vistoria recorrente (L12) · câmera medindo progresso ou EPI (Onda 3, R&D) · análise
de IA da reunião de obra.

⚠️ **Não copie copy da UI do ERP.** O empty state do próprio sistema promete "o encarregado
manda áudio e foto por WhatsApp" — isso é roadmap, não código.

O guard `.github/scripts/seo.py` reprova o push que escrever qualquer uma. Ele também
reprova prova social inventada, métrica de economia sem estudo, concorrente pelo nome e
marcador de rascunho.

## Cicatrizes (bugs reais desta base e das irmãs)

- **`git diff --quiet` não vê arquivo untracked.** O `livreto.yml` decidia assim se
  commitava o espelho; num repo novo o `livreto.pdf` nasce untracked, então o job gerava as
  19 páginas, passava no guard de página em branco e dizia "nada mudou" — `/livreto.pdf`
  respondia 404 sem nenhum workflow vermelho. Hoje usa `git status --porcelain`.
- **Foto de fundo atrás de texto no mobile** vira borrão. O hero põe texto em campo sólido e
  a foto **inteira** embaixo. Não "resolva" com opacidade.
- **Evite scroll-snap horizontal em bloco alto** — no Chrome/Android o dedo fica preso no
  contêiner que rola na horizontal.
- **Escopo de CSS vaza**: um `.ft a{text-decoration:underline}` grifou o logotipo do rodapé.
- **Crop central decapita.** As fotos saem 3:2 do gerador e o hero é 16:9 — o corte tira topo
  e base, e é no topo que estão as cabeças. O hero usa âncora 0.12.
- **Referenciar foto que não existe não quebra nada visível.** `bento-art` e `bento-equipe`
  foram para produção como `<img>` 404 dentro do PDF; o guard de página em branco não pega,
  porque a página tem texto. Ao adicionar `foto("x")` no livreto, confira `assets/x.jpg`.

## Imagens

**Doutrina: foto = gerador de imagem, UI = HTML/CSS.** Nunca peça interface ao gerador —
ele alucina texto ("Entrda 09:2A") e borra a tipografia. O painel da seção "No comando" é
HTML/CSS à mão, e leva `<figcaption>` dizendo que é exemplo: sem isso, "R$ 148.000 de
R$ 255.000" ao lado de um nome de obra lê como cliente real.

As fotos são geradas pela cadeia do ERP (`Auto::Imagens::Gerador`, que já roda em produção
para o blog), com prompts que **proíbem tela legível na cena** — o assunto é canteiro:
andaime, capacete, prancheta, fachada. Depois são cortadas e otimizadas para JPEG
progressivo. **Amplie antes de aprovar**: uma foto com o celular de costas para o próprio
dono já foi ao ar numa das irmãs.

## Como verificar

- **Layout**: screenshot em **1440px e 412px**. Vários bugs só existem no mobile.
- **Guard**: `python3 .github/scripts/seo.py` local, e force uma violação de propósito para
  ver o vermelho — "um workflow que nunca foi executado não vale nada".
- **Produção**: compare o artefato local com o que o servidor entrega (o `diff` do topo).
