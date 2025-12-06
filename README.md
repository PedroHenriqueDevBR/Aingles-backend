# Aingles Backend

Backend do aplicativo Aingles, facilita a sincronização da aplicação entre diferentes plataformas.

## 🔐 Autenticação JWT

Este projeto implementa autenticação JWT (JSON Web Tokens) com banco de dados SQLite local.

### Configuração Rápida

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com sua chave secreta JWT
```

3. Execute o servidor:
```bash
fastapi dev main.py
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Endpoints Principais

### Autenticação
- `POST /auth/signup` - Registrar novo usuário
- `POST /auth/signin` - Login
- `POST /auth/signout` - Logout
- `GET /auth/me` - Obter dados do usuário atual
- `POST /auth/refresh` - Atualizar token
- `GET /auth/verify` - Verificar validade do token

### Recursos
- `GET /article` - Listar artigos
- `GET /card` - Listar cards

## 🛠️ Tecnologias

- **FastAPI** - Framework web
- **SQLite** - Banco de dados local
- **SQLModel** - ORM
- **python-jose** - Criação e validação de tokens JWT
- **passlib** - Hash de senhas com bcrypt
- **PyJWT** - Validação de tokens JWT

## 📖 Configuração de Autenticação

1. Gere uma chave secreta segura:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Configure a variável de ambiente `JWT_SECRET` no arquivo `.env`:
```
JWT_SECRET=sua-chave-secreta-gerada-aqui
```

3. O banco de dados SQLite será criado automaticamente na primeira execução
4. Nunca commite o arquivo `.env` no controle de versão
