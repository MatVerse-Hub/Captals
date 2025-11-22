# Instalação do Ξ-LUA v2.0 LUA-AutoHeal

## Requisitos

### Python 3.8+

```bash
python3 --version  # Deve ser >= 3.8
```

### Dependências Python

```bash
pip3 install --user cryptography>=41.0.0
```

**Nota**: Se encontrar erro `ModuleNotFoundError: No module named '_cffi_backend'`, reinstale cryptography:

```bash
pip3 uninstall cryptography
pip3 install --user --force-reinstall cryptography
```

Ou use um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
pip install cryptography
```

## Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/MatVerse-Hub/test.git
cd test

# 2. Instale dependências
pip3 install --user cryptography

# 3. Torne o CLI executável
chmod +x ξ-lua

# 4. Teste
./ξ-lua heal-test
```

## Instalação via Script

```bash
curl -fsSL https://matverse.sh/install | bash
```

## Verificação da Instalação

```bash
# Verificar Python
python3 --version

# Verificar cryptography
python3 -c "from cryptography.hazmat.primitives.ciphers.aead import AESGCM; print('Cryptography: OK')"

# Verificar CLI
./ξ-lua status
```

## Solução de Problemas

### Erro: ModuleNotFoundError: No module named '_cffi_backend'

**Causa**: Bindings Rust/CFFI da biblioteca cryptography corrompidos

**Solução 1** (Preferida - Virtual Environment):
```bash
python3 -m venv ~/.xi-lua-venv
source ~/.xi-lua-venv/bin/activate
pip install cryptography
```

**Solução 2** (Reinstalar):
```bash
pip3 uninstall cryptography cffi
pip3 install --user --upgrade --force-reinstall cryptography cffi
```

**Solução 3** (Usar distribuição do sistema):
```bash
# Ubuntu/Debian
sudo apt-get install python3-cryptography

# Fedora/RHEL
sudo dnf install python3-cryptography

# Arch
sudo pacman -S python-cryptography
```

### Erro: Permission denied

```bash
chmod +x ξ-lua
chmod +x xi-lua/scripts/*.sh
chmod +x xi-lua/scripts/*.py
```

### Erro: Command not found

Adicione ao PATH:
```bash
echo 'export PATH="$PATH:$HOME/test"' >> ~/.bashrc
source ~/.bashrc
```

## Dependências Opcionais

### Para TemporalAnchor (Smart Contract)

```bash
npm install -g hardhat
npm install @openzeppelin/contracts
```

### Para MatVerse-Copilot

```bash
pip3 install --user web3 requests python-dotenv
```

## Estrutura de Diretórios

Após instalação, você terá:

```
~/.xi-lua/
├── master.key           # Master key (auto-gerada, 600 permissions)
├── autoheal.log         # Merkle-chain logs
└── config.json          # Configurações (futuro)
```

## Configuração Inicial

```bash
# 1. Iniciar AutoHeal (gera master key)
./ξ-lua heal-test

# 2. Verificar status
./ξ-lua status

# 3. Ver logs
./ξ-lua logs -n 10
```

## Performance

- **Rotação de chave**: <1s
- **Criptografia/descriptografia**: <10ms
- **Verificação Merkle**: <50ms para 10k entradas
- **Memória**: ~50MB (incluindo Python runtime)

## Segurança

- **Master key**: Armazenada em `~/.xi-lua/master.key` com permissões 600
- **Logs**: Imutáveis via Merkle-chain SHA-3
- **Rotação**: Automática a cada 5 minutos (300s)
- **Kill-switch**: Ativado após 3 eventos suspeitos em 60s

## Próximos Passos

1. Leia a documentação: [LUA-AUTOHEAL.md](./LUA-AUTOHEAL.md)
2. Execute demo: `./xi-lua/scripts/demo_autoheal.sh`
3. Rode testes: `python3 ./xi-lua/scripts/test_autoheal.py`
4. Integre no seu projeto

## Suporte

- GitHub Issues: https://github.com/MatVerse-Hub/test/issues
- Documentação: [README.md](./README.md)
- Detalhes técnicos: [LUA-AUTOHEAL.md](./LUA-AUTOHEAL.md)
