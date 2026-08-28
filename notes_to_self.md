# Notas quanto à arquitetura hexagonal

- Decidir remover este arquivo do .gitignore, ele possui notas que tomo enquanto desenvolvo a aplicação. A ideia é me
  ajudar com os pontos que não ficaram muito claros da arquitetura hexagonal

> Portas são as ***interfaces***, adaptadores são as ***implementações***

## Nomeclaturas

## Quanto a tipos

## primary ou driving ou api ou in

- São os casos de uso, o que aciona o app

## secondary ou driven ou spi(service provider interface) ou out

- São aquilo que o app aciona

> Ex.: persistencia

---

# Progresso (atualizado 2026-08-12)

## Decisões firmadas

- **Objetivo: aprender hexagonal à risca + auth de ponta a ponta.** Não é pra "entregar rápido" — a cerimônia é o exercício. (Não reescrever em MVC/Java.)
- **Mapeamento ORM: Opção B** — model ORM separado + mapper. Domínio nunca herda de `Base`.
- **Banco: SQLite** pra v1 (troca pra Postgres depois = mudar URL + driver).
- **Sync** (não async).
- **Sem Unit of Work** — decisão revertida. `SqlUserRepository.save` comita direto (commit-on-save), use cases seguem dependendo do `UserRepository` diretamente.
- **Roles: enum em memória (`UserRole`), guardado como coluna JSON `list[str]`** — sem tabela de roles. Perde query "todos os admins", mas atende o caso atual.
- **Adapter de entrega deferido** até o hexágono fechar (provável FastAPI; Basic Auth usa `VerifyUserCredentials`, login JWT usa `AuthenticateUser`).

## Feito

### Domínio (`core/domain`)

- `User` (entidade rica: roles, ativar/desativar, updates, `__eq__` por id) — documentado.
- `UserRole` (StrEnum ADMIN/USER) — documentado.
- `exceptions.py` (família `DomainException`, 11 subclasses) — documentado.

### Portas primárias (`core/ports/primary/user.py`) — documentadas

- 9 protocolos: CreateUser, GetUser, UpdateUserFullName, UpdateUserEmail, ChangeUserPassword, ResetUserPassword, RegisterUser, AuthenticateUser, VerifyUserCredentials.
- `AuthResult` (VO: user + access_token).

### Portas secundárias (`core/ports/secondary`) — documentadas

- `UserRepository`, `PasswordHasher`, `TokenIssuer`.

### Use cases (`core/use_cases`) — implementados + documentados + testados

- CreateUser, GetUser, UpdateUserFullName, UpdateUserEmail, ChangeUserPassword,
  ResetUserPassword, RegisterUser, VerifyUserCredentials, AuthenticateUser.
- Testes unitários com fakes (`FakeUserRepository`, `FakePasswordHasher`, `FakeTokenIssuer`) + `conftest`. Todos verdes.
- Segurança já pensada: `InvalidCredentials` uniforme (sem enumeração), timing uniforme no verify (hash+verify dummy no ramo de user inexistente).

### Adapter de persistência (`adapters/secondary/persistence`) — completo

- `UserModel` (models.py) — pronto e documentado.
- `mapper.py` (`user_to_user_model` / `user_model_to_user`) — pronto e documentado. Trata roles (set↔list ordenada) e reata UTC na leitura.
- `SqlUserRepository` (`__init__.py`) — implementa `UserRepository` usando `session` + mapper na fronteira; `save` comita direto (sem UoW), traduz `IntegrityError` em `UserAlreadyExists`.
- `db.py` — engine + `sessionmaker` + URL via `Settings`.
- Testes de **integração** (`tests/integration/test_orm.py`, SQLite) cobrindo save/get/duplicidade — todos verdes.

### Adapters de segurança (`adapters/secondary/security`) — completo

- `Argon2PasswordHasher` — implementa `PasswordHasher` via `argon2-cffi`.
- `JwtTokenIssuer` — implementa `TokenIssuer` via `PyJWT`; claims `sub`/`roles`/`iat`/`exp`, secret/algoritmo/expiração vêm de `Settings` (`JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES`).
- Testes de integração (`tests/integration/test_security.py`) — todos verdes.

## Falta

- Método de **verificação** de token recebido no `TokenIssuer` (validar request e reconstruir o actor) — ainda não implementado, necessário pro adapter de entrega.

### Adapter de entrega (primário)

- FastAPI (ou equivalente): adapter Basic Auth (usa VerifyUserCredentials) e login JWT (usa AuthenticateUser).

### Deferidos / futuro

- Fluxo "esqueci a senha" (depende de adapter de e-mail).
- Diagramas: ER/relacional (após persistência), sequência do fluxo de auth, diagrama do hexágono.
