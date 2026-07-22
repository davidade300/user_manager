# O que é o user manager ?

- Um crud simples de usuários com roles, incluindo um portal admin para crud de usuários.

## Por que do projeto ?

- A ideia é ter algo semelhante ao Django admin, para que eu possa reutilizar em meus projetos que podem requerer
  usuários. Ou seja, o projeto é um boilerplate de users-admin.

> Por mais que o django admin já exista, dentro do ecosistema Django, e seja uma solução testada e aprovada, eu não
> tenho o costume de utilizar o framework.

- Acredito que é o tipo de projeto ideal para aplicar arquitetura hexagonal, algo que venho estudando recentemente
  (07/2026), posso ter um domínio limpo, com todas as dependências apontada para ele.

## Decisões arquiteturais:

- Por mais que ser pragmático em nível de arquitetura seja o ídeal, desenvolverei esse projeto seguindo a ideia de
  arquitetura hexagonal a risca. Usarei SQLAlchemy para mapeamento relacional, mas farei com mapeamento imperativo,
  mantendo o domínio livre de qualquer forma de acoplamento.
- Tomarei as demais decisões ao longo do desenvolvimento do projeto, adicionarei as mesmas aqui no readme quando eu
  tomá-las.

> Para documentação/ diagramas, ver diretorio app_docs
