-- 0009 · Coherencia de estado de casos
-- Los campos de cierre (closed_at, finished_at, completion) solo tienen sentido
-- en casos CERRADOS. Si un caso fue reabierto (o quedó con datos "sellados" de
-- un cierre previo), se limpian para que TODAS las estadísticas reflejen el
-- estado actual y no un cierre que ya no aplica. Idempotente: se puede correr
-- varias veces sin efecto adicional.
update cases
set closed_at   = null,
    finished_at = null,
    completion  = null
where status <> 'closed'
  and (closed_at is not null or finished_at is not null or completion is not null);
