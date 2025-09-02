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

# 1. Testa conexão com GitHub
if ssh -T git@github.com -o StrictHostKeyChecking=no 2>&1 | grep -q "successfully authenticated"; then
    log "Conexão com GitHub verificada."
else
    log "❌ Falha na conexão SSH com GitHub. Backup abortado."
    exit 1
fi

# 2. Adiciona mudanças
git add . >> /dev/null 2>&1

# 3. Faz commit se houver mudanças
if git commit -m "Backup automático em $NOW" >> /dev/null 2>&1; then
    # 4. Tenta enviar para o repositório remoto
    if git push origin main >> /dev/null 2>&1; then
        log "✅ Alterações commitadas e enviadas com sucesso."
    else
        log "❌ Commit feito, mas falha ao enviar para o GitHub."
    fi
else
    log "Nenhuma alteração detectada, nada para commit."
fi

