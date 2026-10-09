# Receipt Raven backend

FastAPI + SQLAlchemy (async) + PostgreSQL, laid out as Domain-Driven Design with
hexagonal boundaries. See the root `README.md` for commands and `CLAUDE.md` for
the architecture rules.

```
src/
  domain/          entities, value objects, domain exceptions (no framework imports)
  application/     use cases (commands/ and queries/) and ports (protocols/)
  infrastructure/  ORM models, repositories, query adapters, routers, schemas
  containers/      dependency-injector wiring
  main.py          FastAPI app
```
