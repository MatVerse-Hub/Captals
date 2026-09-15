# Instrumented State Machine (Rust)

`InstrumentedStateMachine<S>` é uma classe genérica para transições de estado de alta frequência com métricas atômicas, sampling de observabilidade e batching assíncrono.

## Propriedades

- Estado genérico `S` protegido por `RwLock`.
- Lógica de negócio executada **fora** do lock.
- Commit do novo estado somente após `Ok(())`.
- Métricas `AtomicU64` com `Ordering::Relaxed`.
- Falhas sempre são instrumentadas.
- Sucessos são amostrados por `sample_rate` e por limiar de duração.
- Batch worker assíncrono em canal Tokio; a transição não faz `await` para emitir telemetria.
- Sem `unsafe` e sem dependências além de `tokio`, `tracing` e `std`.

## Uso

```bash
cd captals/instrumented-state-machine-rust
cargo run
cargo test
```

O exemplo executa 10.000 transições de um `OrderState` e simula falhas de negócio.

## API principal

```rust
let (machine, worker) = InstrumentedStateMachine::with_unbounded_batching(
    initial_state,
    SamplingConfig {
        sample_rate: 1_000,
        min_duration_ms: 2,
    },
    BatchConfig::default(),
);

let result = machine.transition(next_state, || {
    // lógica de negócio pura
    Ok(())
});
```

## Por que `RwLock`

Leituras de snapshot podem ocorrer em paralelo e o write lock só é mantido no commit final. A closure de negócio não roda sob lock, reduzindo contenção. Isso produz semântica de **última transição bem-sucedida que conclui vence** quando várias threads chamam `transition` concorrentemente.

Para uma máquina de estados com ordem estritamente linearizável, use um ator de estado único ou serialize chamadas com um mutex externo. Não esconda esse requisito: throughput e ordem total são escolhas de arquitetura diferentes.

## Sampling e performance

`#[instrument]` em cada transição cria/entra em spans por chamada e normalmente registra argumentos via `Debug`. Neste módulo, o macro `tracing::event!` só é executado quando a transição falha, fica lenta ou passa pela regra de sampling.

Isso separa:

```text
hot path: contador atômico → lógica → commit curto
cold path: evento amostrado → canal → batch → tracing
```

## Batching

O modo `with_unbounded_batching` usa `tokio::sync::mpsc::unbounded_channel`. O envio é imediato e não aplica backpressure à thread de transição. O custo é risco de crescimento de memória se o consumidor ficar atrasado.

Para produção com limite rígido de memória, troque o canal por `tokio::sync::mpsc::channel(capacidade)` e use `try_send`, incrementando uma métrica de eventos descartados quando o buffer estiver cheio.

## Tokio Console

A crate não inicializa subscriber: isso é responsabilidade do binário hospedeiro. Em um binário de desenvolvimento, adicione `console-subscriber` e chame uma vez, antes de criar qualquer task:

```rust
console_subscriber::init();
```

Use filtros para manter o console útil:

```text
RUST_LOG=instrumented_state_machine=info,meu_dominio=debug
```

Os eventos de negócio usam os targets `instrumented_state_machine.transition` e `instrumented_state_machine.batch`; o console pode continuar focado em tasks Tokio enquanto o batch reduz poluição de eventos.

## Limites deliberados

- O worker de batch agrega eventos já selecionados; ele não altera decisões de negócio.
- Erros retornados pela closure permanecem com o chamador; o batch registra apenas `OK`/`ERR`, sem serializar detalhes de erro.
- A métrica atômica é observacional. Ela não fornece uma transação global entre estado e contadores.
