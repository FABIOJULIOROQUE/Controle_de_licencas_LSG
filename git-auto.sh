#!/bin/bash
# Script para automatizar commits e push no GitHub

# Ir para a pasta do projeto
cd ~/Controle_de_licencas_LSG || exit

# Adicionar todos os arquivos
git add .

# Commit com data/hora
git commit -m "Atualização automática - $(date '+%Y-%m-%d %H:%M:%S')"

# Enviar para o repositório remoto
git push -u origin main
