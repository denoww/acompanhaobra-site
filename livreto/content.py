# -*- coding: utf-8 -*-
"""Conteúdo do livreto do acompanhaobra — 95% das mudanças acontecem AQUI.

VOCÊ SÓ PRECISA EDITAR ESTE ARQUIVO. O HTML e o PDF se regeneram sozinhos no CI
(.github/workflows/livreto.yml) assim que você der push — o PDF é um ESPELHO
automático. Não rode build.py nem build_pdf.sh na mão; se rodar, o CI só confirma
que já estava em dia. O CI ainda abre o PDF e barra o build se alguma página sair
EM BRANCO (a falha clássica do @media print, que quebra em silêncio).

Fonte da verdade factual, nesta ordem de precedência:
  1. `app/services/obras/ROADMAP.md` no repo do ERP (denoww/seucondominio) — é o
     que diz o que está ENTREGUE e o que é roadmap. Nada entra aqui sem estar lá.
  2. `app/services/obras/CLAUDE.md` — as decisões de arquitetura do módulo.
  3. `livreto/build/content.py` do ERP (o /livreto/obras) — a mesma copy, na voz
     do produto inteiro. Este livreto é o recorte de UMA dor.

⛔ REGRAS DE COPY — o que NÃO pode ser prometido (conferido em 2026-08-19; todos
   seguem com o checkbox aberto no ROADMAP.md do módulo). O guard
   `.github/scripts/seo.py` reprova o push que escrever qualquer uma:

  • RDO / diário de obra por WhatsApp com áudio transcrito (L7b). O diário é
    preenchido NA TELA. ⚠️ o empty state do próprio ERP promete WhatsApp — não
    copie copy da UI para cá.
  • App de campo ou PWA do mestre de obras (L24c, L25). A equipe externa entra
    pelo NAVEGADOR, por link de convite.
  • Cotação que ENVIA e-mail ao fornecedor (L10b). O sistema GERA o link; o
    síndico manda. Escreva "cada fornecedor recebe um link", nunca "o sistema envia".
  • Status de EFD-Reinf POR OBRA na tela (L17). ⚠️ regra de LADO ÚNICO: a retenção
    de INSS na parcela e a geração/transmissão do R-2010 SÃO reais e podem ser
    ditas — o que não existe é o filtro/badge por obra.
  • Retenção contratual de 5–10% como garantia (L27), liberar garantia (L31),
    vincular obra ao patrimônio (L32), vistoria recorrente (L12).
  • Câmera medindo progresso da obra ou detectando EPI (Onda 3, R&D).
  • Análise de IA da reunião de obra — o adapter existe, o frontend não consome.

  Além disso, como em todas as peças da casa: nada de prova social inventada
  ("X condomínios"), nada de concorrente pelo nome, nada de número não verificado.
"""

# O número vive em UM lugar só: o arquivo `.whatsapp` na raiz do repo. Dotfile não é
# publicado pelo GitHub Pages, e o workflow `guarda.yml` barra o push se algum `wa.me`
# do HTML divergir dele. Trocou de número? Edite `.whatsapp` e mais nada aqui.
from pathlib import Path

WA = "https://wa.me/" + (Path(__file__).parent.parent / ".whatsapp").read_text().strip()
WA_TXT = "?text=Ol%C3%A1%21%20Vi%20o%20livreto%20do%20acompanhaobra%20e%20quero%20conhecer."
SITE = "https://www.acompanhaobra.app"

# ---------------------------------------------------------------- hero / credo
HERO = {
    "eyebrow": "Livreto",
    "h1": "A obra deixa de morar no WhatsApp.",
    "sub": "Cotação, contrato, etapas, medição e aditivo no mesmo lugar. E a reforma do "
           "morador seguindo a NBR 16280 — com o termo assinado que protege o síndico "
           "depois, quando alguém perguntar quem autorizou o quê.",
}

CREDO = ('Da primeira cotação ao termo de conclusão, cada etapa fica registrada — e o que '
         '<span class="g">protege o síndico</span> sai assinado, não combinado.')

# ---------------------------------------------------------------- storyboards
# (chave, capítulo-cor, título, [(cena, título, legenda)])
BOARDS = {
    "obra": ("terra", "Da cotação ao termo, sem nada acertado só no verbal", [
        ("cotacao",  "Cota com quem quiser", "Cada fornecedor recebe um link e responde sem criar login."),
        ("contrato", "Contrata e assina",    "Contrato, projeto e ART ficam anexados à obra, assinados."),
        ("etapas",   "Divide em etapas",     "Cada marco tem data prevista e percentual executado."),
        ("medicao",  "Mede e paga",          "A medição do mês vira parcela, com o INSS retido sozinho."),
        ("termo",    "Encerra assinado",     "Síndico e empreiteiro assinam. Só então a obra fecha."),
    ]),
    "nbr": ("petroleo", "A reforma do vizinho, do pedido ao termo", [
        ("morador",  "O morador solicita",   "Pelo mesmo aplicativo do boleto, com projeto e ART anexados."),
        ("ia",       "A IA lê a ART",        "Engenheiro, CREA ou CAU, número, área e intervenção estrutural."),
        ("checklist","O checklist da norma", "O sistema mostra o que falta, separando crítico de aviso."),
        ("assina",   "Aprova com termo",     "Síndico e morador assinam as condicionantes antes de começar."),
    ]),
    "fiscal": ("ambar", "Quando a obra do morador atrapalha o prédio", [
        ("foto",     "Registra com foto",    "Areia na rua, caçamba fora de hora, obra no domingo."),
        ("prazo",    "Dá prazo e gravidade", "A notificação diz o que acontece se o prazo passar."),
        ("infracao", "Vira infração",        "Não regularizou? Escala para advertência ou multa."),
    ]),
}

# ---------------------------------------------------------------- capítulos
# (título, descrição, selo)  — selo "" = produção. Nunca vender roadmap como pronto.
OBRA = [
    ("Cotação por link",
     "Cada fornecedor recebe um link e responde a proposta sem criar login nem instalar nada. "
     "As respostas chegam lado a lado, para escolher o vencedor.", ""),
    ("Contrato e documentos",
     "Contrato, projeto, ART e nota ficam anexados à obra. O que precisa de assinatura vai "
     "assinado e volta arquivado, sem sair do sistema.", ""),
    ("Etapas com prazo",
     "A obra é dividida em marcos, cada um com data prevista e percentual executado. O progresso "
     "da obra é a soma deles, não um chute.", ""),
    ("Aditivo rastreável",
     "Mudou o escopo? O aditivo é gerado, assinado pelas partes e aplicado na próxima parcela do "
     "empreiteiro — não vira um acerto verbal.", ""),
    ("Termo de conclusão",
     "No fim, síndico e empreiteiro assinam. A obra só passa a concluída quando as duas "
     "assinaturas entram.", ""),
    ("O histórico do prédio",
     "Toda obra concluída fica na linha do tempo do edifício. O próximo síndico não começa do "
     "zero, nem pergunta quem fez a fachada em 2019.", ""),
]

UNIDADE = [
    ("O morador solicita",
     "Ele abre a reforma pelo mesmo aplicativo do boleto e anexa projeto e ART. O síndico recebe "
     "para analisar, em vez de caçar papel na conversa.", ""),
    ("A ART é lida por IA",
     "Do PDF saem o engenheiro, o CREA ou CAU, o número da ART, a área e se há intervenção "
     "estrutural — sem ninguém digitar.", "IA"),
    ("O checklist da norma",
     "O sistema confere o que a NBR 16280 exige e mostra o que falta, separando o que é crítico "
     "do que é só aviso.", ""),
    ("Aprovação com termo",
     "Síndico e morador assinam as condicionantes antes de a obra começar. O síndico pode aprovar "
     "direto — mas é o termo que o protege depois.", ""),
    ("Conclusão com garantia",
     "No fim, o termo de conclusão registra a garantia e a quitação de danos, assinado pelos dois.", ""),
    ("Construção no lote vazio",
     "Em loteamento e condomínio horizontal, a casa erguida do zero é um terceiro tipo de obra, "
     "com as categorias e o acompanhamento dela.", ""),
    ("A reforma do vizinho é privada",
     "O morador vê as obras do condomínio e as da unidade dele. A reforma alheia aparece sem "
     "descrição e sem valor.", ""),
]

EQUIPE = [
    ("O engenheiro entra no sistema",
     "Ele recebe um convite por e-mail, clica e cai direto na obra dele. Sem senha para inventar "
     "no primeiro acesso, sem chamado com o suporte.", ""),
    ("Ele vê só a obra dele",
     "Nada do resto do condomínio: nem o financeiro, nem os moradores, nem as outras obras. O "
     "acesso nasce restrito.", ""),
    ("Sobe documento e foto",
     "ART, contrato, nota e a foto do dia entram por ele — sem se perder no meio da conversa do "
     "grupo.", ""),
    ("Fica registrado quem enviou",
     "Cada documento, foto e diário mostra o nome e o papel de quem subiu. Se alguém perguntar "
     "depois, a resposta está na tela.", ""),
    ("Cinco papéis",
     "Engenheiro, empreiteiro, mestre de obras, fiscal e outros — cada um com a sua cor na tela "
     "do síndico.", ""),
    ("Acaba a obra, acaba o acesso",
     "Concluiu, os acessos da equipe externa se encerram sozinhos. O síndico também tira o acesso "
     "em um clique, e o convite que ninguém usou expira em trinta dias.", ""),
]

FISCAL = [
    ("Notificação com foto",
     "Areia na rua, caçamba fora de hora, obra no domingo. O gestor registra com foto e prazo "
     "para regularizar — e o morador não alega que ninguém avisou.", ""),
    ("Itens padronizados",
     "O condomínio cadastra o catálogo de infrações uma vez. Na notificação é só marcar — e o que "
     "foi marcado fica congelado nela, mesmo que o catálogo mude depois.", ""),
    ("Gravidade e prazo",
     "Baixa, média, alta ou crítica, com o prazo de regularização junto. A notificação diz o que "
     "acontece se o prazo passar.", ""),
    ("Vira infração quando precisa",
     "Não regularizou? A notificação escala para a infração do módulo administrativo, herdando "
     "gravidade, itens e morador — e segue para advertência ou multa.", ""),
]

DINHEIRO = [
    ("Pagamento por medição",
     "A medição do mês é uma parcela. O empreiteiro é o mesmo cadastro de fornecedor que o "
     "financeiro do condomínio já usa.", ""),
    ("O INSS é retido sozinho",
     "A retenção entra na parcela sem o síndico precisar saber calcular. Ele não vira contador "
     "para pagar a obra.", ""),
    ("EFD-Reinf transmitido",
     "O evento de retenção é gerado e transmitido ao governo pelo próprio sistema, junto com os "
     "outros do mês.", ""),
    ("O CNO no lugar certo",
     "O cadastro da obra na Receita fica guardado na obra — e o sistema avisa quando há pagamento "
     "com INSS sem CNO, antes de virar autuação.", ""),
    ("O passado do empreiteiro",
     "Ao escolher o empreiteiro, o sistema mostra o que ele já fez neste condomínio: quanto "
     "atrasou, quanto estourou do orçado e a nota que ele tirou.", ""),
    ("Orçado contra realizado",
     "O que foi aprovado e o que já saiu do caixa, lado a lado, com o percentual executado. O "
     "estouro aparece enquanto dá para reagir.", ""),
]

PAINEL = [
    ("O painel da obra",
     "No prazo contra fora do prazo, tempo médio até concluir e a saúde da carteira — em vez de "
     "abrir uma obra por uma para saber como vão.", ""),
    ("Sete cards de operação",
     "Aprovação parada, aditivo sem assinatura, cotação sem resposta, pagamento vencendo, marco "
     "atrasando, início atrasado. Cada card filtra a lista.", ""),
    ("O alerta antes da cobrança",
     "Marco vencido e obra que não começou viram aviso para quem pode agir — no aplicativo, por "
     "e-mail ou no WhatsApp, como você escolher.", ""),
    ("A linha do tempo",
     "O previsto e o realizado, mês a mês, no mesmo gráfico. Dá para ver o atraso nascendo, não "
     "descobrir no fim.", ""),
    ("Relatório em um clique",
     "O PDF da obra com a logo do condomínio, pronto para a assembleia: resumo, orçamento, "
     "marcos, pagamentos, aditivos e diários.", ""),
    ("Tudo em um feed só",
     "Diário, foto e vídeo em ordem cronológica, com autor e data. O vídeo toca na própria "
     "página, sem baixar nada.", ""),
    ("A carteira inteira",
     "A administradora vê as obras de todos os condomínios dela numa tela só, sem trocar de "
     "prédio a cada consulta.", ""),
]

# Para quem é: (slug da foto, rótulo, dor concreta do ICP)
SETORES = [
    ("setor-fachada",    "Prédio residencial", "Fachada, telhado, elevador e garagem — obra grande, dinheiro do rateio e assembleia cobrando."),
    ("setor-reforma",    "Reforma de unidade", "O morador quebra parede sem avisar, e a norma põe a responsabilidade no colo do síndico."),
    ("setor-loteamento", "Loteamento",         "Casa erguida do zero no lote vazio, com regra de obra para fazer valer e vizinho reclamando."),
    ("setor-carteira",   "Administradora",     "Dezenas de obras espalhadas por vários prédios, cada uma num grupo de WhatsApp diferente."),
]

DORES = [
    "A obra mora num grupo de WhatsApp: foto some, combinado vira boato e ninguém acha o contrato.",
    "O morador começou a reforma no sábado e o síndico só soube pela poeira no corredor.",
    "A assembleia pergunta quanto já foi pago e a resposta depende de alguém abrir a pasta certa.",
    "O empreiteiro pediu mais dinheiro no meio da obra e o aditivo ficou no verbal.",
    "Pagou o empreiteiro sem reter INSS — e a conta chega depois, com multa.",
    "Trocou o síndico e o histórico do prédio foi junto: ninguém sabe quem fez a fachada, nem com que garantia.",
]

# Compliance — o que sustenta a decisão do síndico se alguém questionar.
COMPLIANCE = [
    ("NBR 16280 — reforma em edificação",
     "A norma exige plano de reforma, responsável técnico com ART ou RRT e autorização formal "
     "antes de a obra começar. O fluxo do sistema é desenhado em cima disso.", ""),
    ("O síndico decide, e fica registrado",
     "A leitura da IA é orientativa: quem aprova ou rejeita é o síndico, que pode divergir e "
     "registrar a justificativa. É a decisão dele que fica gravada.", ""),
    ("Termo assinado dos dois lados",
     "Aprovação e conclusão saem com assinatura digital de síndico e morador. É o documento que "
     "responde por que a obra foi autorizada, e sob quais condições.", ""),
    ("Retenção e obrigação acessória",
     "Serviço de construção civil tem retenção de INSS e evento de EFD-Reinf. O sistema calcula "
     "na parcela e gera o evento junto com os outros do mês.", ""),
]

# ---------------------------------------------------------------- preço
PRECO = [
    ("Primeira obra", "Grátis", "uma obra ativa",
     "Para valer, não é teste de 14 dias. Abra a próxima obra do prédio e vá até o termo de "
     "conclusão sem pagar nada."),
    ("Condomínio", "R$ 79", "por mês, por prédio",
     "Obras ilimitadas e usuários ilimitados. A equipe externa convidada não ocupa licença."),
    ("Carteira", "Administradora", "sob proposta",
     "Vários condomínios na mesma carteira, com preço por volume e a visão cruzada das obras."),
]

NAOS = [
    ("Sem implantação",
     "Não tem equipamento para comprar, obra para fazer nem taxa de setup. Você abre a obra e "
     "começa a usar no mesmo dia."),
    ("Sem cobrar por obra",
     "O preço é por condomínio, não por obra aberta. Três reformas de unidade no mesmo mês custam "
     "o mesmo que nenhuma."),
    ("Sem fidelidade",
     "Mês a mês, sem carência e sem multa. O produto tem que segurar você — não o contrato."),
]

# ---------------------------------------------------------------- honestidade
# O capítulo mais importante do livreto. Nunca vender roadmap como pronto:
# se não roda hoje, está aqui. Cada item foi conferido contra o ROADMAP.md do módulo.
NAO_FAZ = [
    ("O diário não entra por WhatsApp",
     "O relatório diário é preenchido na tela do sistema, com as fotos e os vídeos anexados. Não "
     "existe o encarregado mandando áudio e a IA transcrevendo — isso é roadmap, e roadmap não se "
     "vende como pronto.", ""),
    ("Não há aplicativo para a equipe de campo",
     "O engenheiro, o empreiteiro e o mestre entram pelo navegador, por link de convite. Não há "
     "app instalável para eles.", ""),
    ("A cotação não dispara o e-mail",
     "O sistema gera o link público da cotação; quem envia ao fornecedor é você. O que chega de "
     "volta é que fica organizado lado a lado.", ""),
    ("Não há painel fiscal por obra",
     "A retenção de INSS e o evento da EFD-Reinf acontecem de verdade, no fluxo do pagamento. O "
     "que não existe é uma tela que filtre o status fiscal obra por obra.", ""),
    ("Não segura garantia do contrato",
     "Não há como reter um percentual do contrato até o aceite final. O que existe é o termo de "
     "conclusão, que registra a garantia acordada.", ""),
    ("Não é orçamento de engenharia",
     "Não há composição de custo unitário nem tabela de referência de preço. O sistema controla o "
     "que foi cotado, contratado, medido e pago — não monta o orçamento da obra para você.", ""),
    ("A câmera não mede a obra",
     "Nenhuma câmera calcula percentual executado nem detecta equipamento de proteção. O "
     "percentual sai dos marcos que a equipe atualiza.", ""),
]

# ---------------------------------------------------------------- lineup
# (nome, descrição, cor, selo)
TILES = [
    ("Cotação por link",   "O fornecedor responde sem criar login.",                 "terra",    ""),
    ("Contrato assinado",  "Assinatura digital, arquivada na própria obra.",         "petroleo", ""),
    ("Etapas com prazo",   "Marcos com data prevista e percentual executado.",       "terra",    ""),
    ("Aditivo rastreável", "Assinado pelas partes e aplicado na parcela seguinte.",  "ambar",    ""),
    ("NBR 16280",          "Solicitação, ART lida por IA, checklist e termo.",       "petroleo", "IA"),
    ("Fiscalização",       "Foto, gravidade e prazo — e escala para infração.",      "ambar",    ""),
    ("Medição com INSS",   "A retenção entra na parcela; o R-2010 sai no mês.",      "terra",    ""),
    ("Equipe externa",     "Convite por e-mail, acesso só àquela obra.",             "petroleo", ""),
    ("Painel e carteira",  "A obra do prédio e as obras de todos os prédios.",       "ambar",    ""),
]

CTA = ("Vamos abrir a sua próxima obra no sistema.",
       "A primeira obra é grátis, do cadastro ao termo de conclusão. Conte qual é a obra do seu "
       "prédio e a gente mostra rodando.")
