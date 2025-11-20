# 📦 Guia de Publicação no PyPI

## Pré-requisitos

Antes de publicar, você precisa:

1. ✅ Conta no PyPI: https://pypi.org/account/register/
2. ✅ Conta no TestPyPI (para testes): https://test.pypi.org/account/register/
3. ✅ Token de API do PyPI (para autenticação segura)

---

## 📋 Checklist Antes de Publicar

- [x] `LICENSE` existe (MIT ✓)
- [x] `README.md` existe e está completo ✓
- [x] `pyproject.toml` configurado corretamente ✓
- [x] Entry point `mcp-yfinance` configurado ✓
- [ ] Versão atualizada no `pyproject.toml`
- [ ] Código testado e funcionando
- [ ] Todos os testes passando (`pytest`)
- [ ] Type checking ok (`mypy src/mcp_yfinance`)
- [ ] Linter ok (`ruff check src/mcp_yfinance`)

---

## 🚀 Método 1: Publicação com `uv` (Recomendado)

O `uv` é mais rápido e moderno que o método tradicional.

### Passo 1: Instalar ferramentas de build

```bash
# O uv já tem tudo que precisa!
# Mas se quiser usar pip, instale:
pip install build twine
```

### Passo 2: Fazer build do pacote

```bash
# Com uv (recomendado)
uv build

# OU com python -m build
python -m build
```

Isso vai criar:
- `dist/mcp_yfinance-0.1.0-py3-none-any.whl` (wheel)
- `dist/mcp_yfinance-0.1.0.tar.gz` (source distribution)

### Passo 3: Testar no TestPyPI primeiro

```bash
# Upload para TestPyPI
twine upload --repository testpypi dist/*

# Você vai precisar:
# Username: __token__
# Password: seu-token-do-testpypi
```

### Passo 4: Testar instalação do TestPyPI

```bash
# Instalar do TestPyPI para testar
pip install --index-url https://test.pypi.org/simple/ mcp-yfinance

# Testar se funciona
mcp-yfinance --help
python -c "from mcp_yfinance import __version__; print(__version__)"
```

### Passo 5: Publicar no PyPI oficial

```bash
# Se tudo funcionou no TestPyPI, publique de verdade!
twine upload dist/*

# Você vai precisar:
# Username: __token__
# Password: seu-token-do-pypi
```

---

## 🔑 Configuração de Token API (Recomendado)

Em vez de usar senha, use tokens API (mais seguro):

### 1. Criar token no PyPI

1. Vá em https://pypi.org/manage/account/token/
2. Clique em "Add API token"
3. Nome: "mcp-yfinance-upload"
4. Scope: "Entire account" (ou específico para o projeto)
5. Copie o token (começa com `pypi-...`)

### 2. Configurar credenciais

**Opção A: Variáveis de ambiente (temporário)**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-seu-token-aqui
twine upload dist/*
```

**Opção B: Arquivo de configuração (permanente)**

Crie `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-seu-token-do-pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-seu-token-do-testpypi
```

Depois é só:

```bash
twine upload --repository testpypi dist/*  # TestPyPI
twine upload dist/*                         # PyPI oficial
```

---

## 🔄 Publicar Nova Versão

Quando quiser publicar uma atualização:

### 1. Atualizar versão

Edite `pyproject.toml`:

```toml
[project]
name = "mcp-yfinance"
version = "0.1.1"  # <- Incrementar aqui
```

E também `src/mcp_yfinance/__init__.py`:

```python
__version__ = "0.1.1"  # <- Incrementar aqui
```

**Versionamento Semântico:**
- `0.1.0` → `0.1.1` - Bug fixes
- `0.1.0` → `0.2.0` - Novas features (compatível)
- `0.1.0` → `1.0.0` - Breaking changes

### 2. Limpar builds antigos

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Fazer novo build e publicar

```bash
uv build
twine upload dist/*
```

---

## 🧪 Método 2: Script Automatizado

Crie `publish.sh`:

```bash
#!/bin/bash
set -e

echo "🧹 Limpando builds antigos..."
rm -rf dist/ build/ *.egg-info

echo "🧪 Rodando testes..."
pytest

echo "🔍 Checando tipos..."
mypy src/mcp_yfinance

echo "📝 Checando linter..."
ruff check src/mcp_yfinance

echo "📦 Fazendo build..."
uv build

echo "✅ Build completo!"
ls -lh dist/

read -p "Publicar no TestPyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Publicando no TestPyPI..."
    twine upload --repository testpypi dist/*
fi

read -p "Publicar no PyPI OFICIAL? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Publicando no PyPI..."
    twine upload dist/*
    echo "✨ Publicado com sucesso!"
fi
```

Tornar executável:

```bash
chmod +x publish.sh
./publish.sh
```

---

## 📊 Após Publicar

### Verificar no PyPI

1. Vá em https://pypi.org/project/mcp-yfinance/
2. Verifique se a página está correta
3. O README.md deve aparecer como descrição

### Testar instalação

```bash
# Criar ambiente limpo
python -m venv test_env
source test_env/bin/activate

# Instalar do PyPI
pip install mcp-yfinance

# Testar
mcp-yfinance --help
```

### Testar com uvx

```bash
# Isso é o que os usuários vão fazer!
uvx mcp-yfinance
```

### Atualizar README

Atualize as instruções de instalação no README.md para remover a parte de "yourusername":

```markdown
## 🚀 Quick Start

### Installation via uvx (Recommended)

```json
{
  "mcpServers": {
    "yfinance": {
      "command": "uvx",
      "args": ["mcp-yfinance"]
    }
  }
}
```

### Manual Installation

```bash
pip install mcp-yfinance
```
```

---

## ⚠️ Problemas Comuns

### "Invalid distribution file"

- Certifique-se que `pyproject.toml` está correto
- Limpe builds antigos: `rm -rf dist/ build/`
- Faça build novamente: `uv build`

### "Package already exists"

- Você não pode substituir uma versão já publicada
- Incremente a versão em `pyproject.toml`
- Publique a nova versão

### "Authentication failed"

- Verifique se o token está correto
- Use `__token__` como username (com dois underscores)
- O token deve começar com `pypi-`

### "README not rendering"

- Certifique-se que `readme = "README.md"` está em `pyproject.toml`
- O README deve estar em Markdown válido
- Use formato GitHub-flavored Markdown

---

## 📝 Resumo Rápido

```bash
# 1. Atualizar versão em pyproject.toml
# 2. Limpar
rm -rf dist/ build/ *.egg-info

# 3. Build
uv build

# 4. Testar (opcional mas recomendado)
twine upload --repository testpypi dist/*

# 5. Publicar
twine upload dist/*

# 6. Verificar
pip install mcp-yfinance
mcp-yfinance --help
```

---

## 🎯 Próximos Passos Após Publicar

1. ✅ Adicionar badge do PyPI no README:
   ```markdown
   [![PyPI version](https://badge.fury.io/py/mcp-yfinance.svg)](https://badge.fury.io/py/mcp-yfinance)
   ```

2. ✅ Criar release no GitHub:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. ✅ Anunciar no MCP Community

4. ✅ Adicionar ao Model Context Protocol server list

---

## 📚 Referências

- **PyPI Upload Guide**: https://packaging.python.org/tutorials/packaging-projects/
- **Twine Docs**: https://twine.readthedocs.io/
- **uv Build**: https://docs.astral.sh/uv/guides/publish/
- **Python Packaging**: https://packaging.python.org/

---

**Boa sorte com a publicação! 🚀**
