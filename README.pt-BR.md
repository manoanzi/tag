# TAG — The Architecture of Gateways

**Um padrão de arquitetura pragmático, funcional e centrado em domínio para microsserviços em Python, incluindo serviços agênticos (LLM).**

[![CI](https://github.com/manoanzi/tag/actions/workflows/ci.yml/badge.svg)](https://github.com/manoanzi/tag/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

🇺🇸 [Read in English](README.md)

> Inspirado em Arquitetura Hexagonal, na arquitetura Diplomata do Nubank e no DOMA da Uber.

---

## Por que TAG

Quando cada time estrutura serviços de um jeito, trocar de contexto custa caro: o onboarding demora, o code review vira debate sobre onde o código deve ficar e o custo de manutenção cresce a cada novo serviço.

O TAG dá a todo serviço o mesmo formato. Quem conhece um serviço TAG se localiza em qualquer outro. Isso importa principalmente para pessoas menos seniores e para áreas que mudam rápido, como GenAI, onde agentes, ferramentas e integrações mudam toda semana.

Ele nasce de experiências em ambientes bem diferentes: construir uma startup de pagamentos do zero, trabalhar nos serviços padronizados em Clojure do Nubank e construir plataformas agênticas como Staff Engineer em GenAI.

## O que é TAG

- **Visão estratégica** (do DOMA): serviços agrupados por domínio de negócio, com gateways como pontos de entrada que escondem os detalhes internos de cada domínio.
- **Visão tática** (do Diplomata e da Hexagonal): todo serviço tem as mesmas camadas, então o código é previsível entre times.

Pilares:

- **Programação funcional:** imutabilidade, funções puras e composição via pipelines
- **Domínio primeiro:** regras de negócio isoladas no centro
- **Tratamento de erros orientado a trilhos:** tipos `Result` no lugar de exceções
- **Injeção de dependência via Protocol:** testável sem infraestrutura
- **Agnóstico de transporte:** HTTP, gRPC, mensageria, streaming ou tool call de um LLM

## Exemplo executável

[`examples/user-service`](examples/user-service) é um serviço completo com todas as camadas do TAG (FastAPI + SQLite, sem infraestrutura externa), com testes unitários, de integração e HTTP:

```bash
cd examples/user-service && pip install -e ".[dev]" && pytest && python -m src.main
```

## Princípios

| # | Princípio | Em resumo |
|---|---|---|
| 1 | Protocols definem contratos | Toda dependência de infraestrutura fica atrás de um `typing.Protocol` |
| 2 | Domains são schemas, nunca funções | Definições de dados imutáveis (Pydantic, `frozen=True`) |
| 3 | Logics são puras e concentram as decisões | Sem IO, aleatoriedade, relógio ou `Result`. Toda regra e ramificação fica aqui, e a decisão volta como schema de domínio (ex.: `UserRuleCheck`) |
| 4 | Adapters transformam estruturas | Conversões puras entre camadas: `model_dump`, linhas do banco, erros, registros de log, respostas e schemas para `Result` (`Success`/`Failure`). Nada de `uuid4()` ou `now()` |
| 5 | Gateways fazem IO | Toda comunicação externa, via Protocols recebidos como parâmetro |
| 6 | Flows são pipelines de orquestração | Um Flow por caso de uso, da entrada bruta ao schema de resposta, compondo Gateways, Logics e Adapters. O log de negócio fica aqui |
| 7 | Handlers só repassam | Entregam a entrada do transporte a um Flow e devolvem o schema de resposta dele. Nada mais |
| 8 | Drivers implementam Protocols | Bibliotecas externas ficam fora do código de domínio |
| 9 | Efeitos colaterais nas bordas | IO passa por Gateways. Aleatoriedade e tempo vêm de Protocols (ex.: `IdGeneratorProtocol`) que o Flow chama direto, entregando o valor a um Adapter |

Nomes: contratos são `<Capacidade>Protocol` (`DatabaseProtocol`, `LoggerProtocol`) e suas implementações são `<Tecnologia>Driver` (`SQLiteDriver`, `UUID4Driver`).

Outras regras:
- **Logs:** eventos de negócio ("usuário criado", "e-mail duplicado") são gravados pelo Flow: um Adapter monta o `LogEntry` e um Gateway grava. Logs de transporte (rota, latência, status HTTP) ficam no Driver.
- **Funções privadas num Flow** só podem compor camadas. Nunca contêm regra, conversão ou IO próprios.
- **Tipos de contrato** (como `LogEntry`) ficam junto do seu Protocol, não em Domains.
- **Resources guardam só configuração:** valores que podem mudar por ambiente ou cliente sem mudar código (listas de bloqueio, mensagens públicas, limites), de preferência em arquivos JSON/YAML (12-Factor, fator III). Queries, esquemas e tabelas de decisão são código: ficam junto de quem os usa (Locality of Behavior). SQL fica no Gateway que o executa, tabelas de decisão na Logic que decide, e DDL em `migrations/`.

## Estrutura de diretórios

```
project-root/
├── src/
│   ├── protocols/   # contratos de infraestrutura (typing.Protocol)
│   ├── domains/     # entidades e objetos de valor (Pydantic)
│   ├── resources/   # configuração: settings e arquivos JSON/YAML
│   ├── logics/      # funções puras de domínio
│   ├── adapters/    # transformações de dados entre camadas
│   ├── gateways/    # IO via Protocols
│   ├── flows/       # pipelines de casos de uso, por domínio
│   ├── handlers/    # pontos de entrada (HTTP, Kafka, cron, tools de agente)
│   └── main.py      # composição
├── drivers/         # implementações de bibliotecas, fora do src/
├── migrations/      # esquema do banco (.sql), aplicado pelo Driver de banco
└── tests/
    ├── unit/        # Adapters e Logics
    └── integration/ # Flows com Protocols em memória
```

## Regras de dependência

| Camada | Pode chamar |
|---|---|
| Protocols, Domains, Resources | nenhuma |
| Logics | Domains, Resources |
| Adapters | Domains, Protocols (só tipos), Resources |
| Gateways | Protocols (única camada que faz IO por eles), Domains, Adapters, Resources |
| Flows | Gateways, Logics, Adapters, Protocols, Resources |
| Handlers | Flows, Protocols |
| Drivers | Protocols, Resources |
| `main.py` | Drivers, Handlers, Resources |

```
Request  → Driver → Handler → Flow → Adapter / Logic / Gateway → Protocol (IO)
Response ← Driver ← Handler ← Flow (response schema)
```

## Exemplo: um caso de uso como Flow

```python
# src/flows/user/create_user_flow.py
def create_user_flow(db, ids, logger, raw: dict) -> CreateUserResponse:
    result = to_create_user_input(raw).bind(                                     # Adapter
        lambda data: flow(
            to_rule_result(check_email_domain(data.email)),                      # Logic + Adapter
            bind(lambda _: find_users_by_email(db, data.email)),                 # Gateway (IO)
            bind(lambda existing: to_rule_result(check_user_is_new(existing))),  # Logic + Adapter
            map_(lambda _: to_user_domain(data, ids.new_id())),                  # Protocol (randomness) + Adapter
            map_(to_user_record),                                                # Adapter
            bind(lambda record: persist_user(db, record)),                       # Gateway (IO)
            map_(to_create_user_output),                                         # Adapter
        )
    )
    write_log(logger, to_create_user_log_entry(result))                          # Adapter + Gateway (IO)
    status = resolve_create_user_status(to_create_user_outcome(result))          # Adapter + Logic
    return to_create_user_response(status, result)                               # Adapter
```

O Flow depende só de Protocols. Até o id do usuário vem do `IdGeneratorProtocol`: gerar o id não é IO, então o Flow chama direto e entrega o valor ao Adapter. Todo Adapter e toda Logic continuam puros e os testes são determinísticos. O [exemplo executável](examples/user-service) injeta Drivers de SQLite e UUIDv4; os testes injetam um banco em memória e um id fixo.

O Handler só repassa: o Flow é dono do caso de uso inteiro, inclusive do log de negócio e do schema de resposta. Logics nunca constroem `Result`; elas devolvem decisões como schemas, e um Adapter as transforma em passos do pipeline.

```python
# src/logics/user_logic.py: decisions as data, never Result
def check_user_is_new(existing: list[UserRecord]) -> UserRuleCheck:
    if existing:
        return UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)
    return UserRuleCheck()

# src/adapters/user_adapter.py: the bridge from schema to Result
def to_rule_result(check: UserRuleCheck) -> Result[None, UserError]:
    return Maybe.from_optional(check.error).map(Failure).value_or(Success(None))
```

```python
# src/handlers/user_handlers.py: only forwards
def handle_create_user(db, ids, logger, raw_body: dict) -> CreateUserResponse:
    return create_user_flow(db, ids, logger, raw_body)
```

```python
# src/main.py
def create_app() -> FastAPIDriver:
    settings = load_settings()
    db, ids, logger, http = SQLiteDriver(settings), UUID4Driver(), StdoutLoggerDriver(), FastAPIDriver()
    register_user_handlers(http, db, ids, logger)
    return http
```

Trocar a infraestrutura é mudar uma linha no `main.py`. Uma tool de agente LLM é só mais um Handler chamando o mesmo Flow.

## Estratégia de testes

| Tipo | Cobre | Infraestrutura |
|---|---|---|
| Unitário | Adapters e Logics (funções puras) | Nenhuma |
| Integração | Flows completos | Protocols falsos, em memória |

Você testa fluxo e regra de negócio, não bibliotecas. A suíte roda sem containers.

## Tratamento de erros

Toda operação que pode falhar retorna `Result[Sucesso, Falha]` ([dry-python/returns](https://github.com/dry-python/returns)). Num pipeline, a primeira falha propaga até o final, sem try/except em cada etapa. O `@safe` encapsula código que lança exceções, como a validação do Pydantic nos Adapters de entrada.

## Evolução de contratos

Adapters de entrada seguem o padrão **Tolerant Reader**: leem só os campos de que precisam, então serviços upstream podem adicionar campos sem quebrar consumidores. Contratos externos podem ser declarados em `resources/` e validados no CI.

## Comparação

| | TAG | Hexagonal | Arquitetura Limpa | DOMA | Diplomata |
|---|---|---|---|---|---|
| Paradigma | Funcional | Agnóstico | OOP | Agnóstico | Funcional (Clojure) |
| Escopo | Serviço + organização | Serviço | Serviço | Organização | Serviço |
| Tratamento de erros | Result | — | — | — | — |
| Injeção de dependência | Protocols | Portas | Interfaces | — | Componentes |

## FAQ

<details><summary><strong>Funciona com qualquer framework HTTP?</strong></summary>

Sim. O framework é um Driver atrás do `HttpServerProtocol`. FastAPI, Flask ou Starlette são trocados no `main.py`.
</details>

<details><summary><strong>Serve para monólitos?</strong></summary>

Sim. Cada domínio ganha sua pasta em `flows/`, e os Protocols mantêm os domínios desacoplados da infraestrutura.
</details>

<details><summary><strong>E async?</strong></summary>

Protocols podem declarar métodos assíncronos, e a `returns` oferece `FutureResult` para operações async que podem falhar.
</details>

## Contribuindo

Contribuições são bem-vindas. Veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT. Veja [LICENSE](LICENSE).
