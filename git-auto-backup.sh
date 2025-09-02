#!/bin/bash
# Script automático de backup para o GitHub
# Fabio - Sistema de Licenças

# Caminho do repositório
REPO_PATH="/home/fabiojulioroque/Controle_de_licencas_LSG"
cd "$REPO_PATH" || exit 1

# Timestamp
NOW=$(date "+%Y-%m-%d %H:%M:%S")

# Função para logar mensagens
log() {
    echo "[$NOW] $1"
}

# Início do backup
log "Backup iniciado..."

# Git add/commit/push
git add . >> /dev/null 2>&1
if git commit -m "Backup automático em $NOW" >> /dev/null 2>&1; then
    if git push origin main >> /dev/null 2>&1; then
        log "Alterações commitadas e enviadas com sucesso."
    else
        log "❌ Falha ao enviar alterações para o GitHub."
    fi
else
    log "Nenhuma alteração para commit."
fi

