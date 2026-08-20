#!/usr/bin/env bash
# =============================================================================
# Emite o certificado do acompanhaobra.app e o pendura no ALB — RODAR NO CLOUDSHELL.
#
# POR QUE NÃO RODA NA MÁQUINA DO DEV
# `acm:RequestCertificate` é negado tanto para o usuário `rodrigo-local` quanto para o
# profile `sec-audit` (que é read-only), e o usuário também não pode ler IAM pra descobrir
# o porquê. O CloudShell roda com a identidade da conta e passa.
#
# O QUE ISTO FAZ
#   1. pede o cert `acompanhaobra.app` + `*.acompanhaobra.app` (validação por DNS)
#   2. cria os CNAMEs de validação na hosted zone do domínio
#   3. espera o ACM emitir (leva de 2 a ~30 min)
#   4. anexa o cert ao listener 443 do ALB `seucondominio-web` (SNI)
#
# O QUE NÃO FAZ (é o passo seguinte, e eu faço daqui)
#   - o A-ALIAS de `blog.acompanhaobra.app` apontando pro ALB
#   - o flip de indexação do blog (`INDEXAVEIS` em app/services/auto/marcas.rb)
#
# É idempotente no que importa: se o cert já existir com esse domínio, ele reaproveita em
# vez de pedir outro (cert duplicado no ALB é confusão na hora de renovar).
#
# Padrão confirmado na conta: `*.baterponto.app` e `*.atendeaqui.app` estão ISSUED e
# pendurados nesse mesmo listener. Este é o terceiro do mesmo tipo.
# =============================================================================
set -euo pipefail

REGIAO="us-east-1"
DOMINIO="acompanhaobra.app"
ZONA="Z04790153ENAI1JMIXFWY"
LISTENER="arn:aws:elasticloadbalancing:us-east-1:516862767124:listener/app/seucondominio-web/b723f96525904587/fb6e1b8f1d20fa86"

echo "==> 1/4 procurando cert existente para $DOMINIO"
ARN=$(aws acm list-certificates --region "$REGIAO" \
        --query "CertificateSummaryList[?DomainName=='$DOMINIO'].CertificateArn | [0]" --output text)

if [ "$ARN" = "None" ] || [ -z "$ARN" ]; then
  echo "    nenhum — solicitando"
  ARN=$(aws acm request-certificate --region "$REGIAO" \
          --domain-name "$DOMINIO" \
          --subject-alternative-names "*.$DOMINIO" \
          --validation-method DNS \
          --query CertificateArn --output text)
  echo "    solicitado: $ARN"
  sleep 15   # o ACM leva alguns segundos pra publicar os registros de validação
else
  echo "    reaproveitando: $ARN"
fi

echo "==> 2/4 criando os CNAMEs de validação na zona $ZONA"
# Um CNAME por nome distinto. O apex e o wildcard costumam compartilhar o MESMO registro,
# daí o `unique` — mandar o mesmo UPSERT duas vezes no mesmo batch é erro no Route53.
aws acm describe-certificate --region "$REGIAO" --certificate-arn "$ARN" \
  --query 'Certificate.DomainValidationOptions[].ResourceRecord.[Name,Value]' --output text \
  | sort -u \
  | while read -r NOME VALOR; do
      [ -z "${NOME:-}" ] && continue
      echo "    $NOME"
      aws route53 change-resource-record-sets --hosted-zone-id "$ZONA" --change-batch "{
        \"Changes\": [{ \"Action\": \"UPSERT\", \"ResourceRecordSet\": {
          \"Name\": \"$NOME\", \"Type\": \"CNAME\", \"TTL\": 300,
          \"ResourceRecords\": [{ \"Value\": \"$VALOR\" }] }}]}" >/dev/null
    done

echo "==> 3/4 esperando o ACM emitir (pode levar ~30 min)"
aws acm wait certificate-validated --region "$REGIAO" --certificate-arn "$ARN"
echo "    ISSUED"

echo "==> 4/4 anexando ao listener 443 do ALB seucondominio-web"
aws elbv2 add-listener-certificates --listener-arn "$LISTENER" \
  --certificates "CertificateArn=$ARN" >/dev/null

echo
echo "PRONTO. Cert: $ARN"
echo "Me avise que eu faço o resto: o DNS de blog.acompanhaobra.app e o flip de indexação."
