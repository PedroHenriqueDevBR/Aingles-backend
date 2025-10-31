# Aingles Backend

Backend do aplicativo Aingles, facilita a sincronização da aplicação entre diferentes plataformas.

## 🔐 Autenticação com Supabase

Este projeto está integrado com **Supabase Authentication** usando o provedor de e-mail.

Para informações completas sobre autenticação, configuração e uso, consulte a [documentação de autenticação](./AUTHENTICATION.md).

### Configuração Rápida

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o .env com suas credenciais do Supabase
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
- **Supabase** - Autenticação e banco de dados
- **SQLModel** - ORM
- **PostgreSQL** - Banco de dados
- **PyJWT** - Validação de tokens JWT

## 📖 Supabase keys

## INSTRUCTIONS FOR SUPABASE AUTHENTICATION SETUP

1. Go to https://app.supabase.com and select your project
2. Navigate to Project Settings > API
3. Copy the following values:
   - URL: Your project URL
   - anon/public key: Your anon key
   - JWT Secret: Your JWT secret (in JWT Settings section)
4. Enable Email Authentication:
   - Go to Authentication > Providers
   - Enable "Email" provider
   - Configure email templates if desired
5. Copy this file to .env and replace the placeholder values
6. Never commit the .env file to version control
