# Splice Drift Audit

## Scope

This document records the first time-resolved body-free audit of the long-window splice drift after the per-cell-type UV-grid alignment fixed the coarse `100 ms` sign error.

Artifacts:

- `outputs/metrics/splice_drift_audit_summary.json`
- `outputs/metrics/splice_drift_audit_timeseries.csv`
- `outputs/metrics/splice_drift_audit_key_findings.json`
- `outputs/metrics/splice_drift_audit_key_findings.csv`

Code:

- `scripts/run_splice_drift_audit.py`

## Question

After `T063`, the remaining question was:

- why does the downstream sign still fail over longer windows?

Three possibilities were live:

1. relay asymmetry itself collapses
2. asymmetry survives to deeper descending pathways, but the fixed tiny DN readout loses it
3. the whole effect is only a short input transient and disappears without a self-sustaining state

## Audit design

The audit uses the sign-correct per-cell-type UV-grid splice:

- `outputs/metrics/splice_celltype_alignment_recommended.json`

It then measures two schedules:

1. `hold`
   - keep the signed visual current on for the whole `500 ms`
2. `pulse_25ms`
   - apply the same input for only `25 ms`, then remove it

It records time-resolved activity for:

- relay groups from `outputs/metrics/splice_relay_candidates.json`
- the fixed tiny DN readout from `src/brain/public_ids.py`
- the broader strict descending/efferent groups from `outputs/metrics/descending_readout_candidates_strict.json`

## Main result

The long-window failure is **not** a complete loss of relay asymmetry.

Under the `hold` schedule:

- fixed DN turn bias is strong and correct at `100 ms`
- but collapses completely by `500 ms`
- meanwhile several relay groups remain strongly contrastive at `500 ms`
- and multiple broader descending groups still carry asymmetric rates at `500 ms`

So the strongest current explanation is:

- the old long-window failure is mainly a **fixed-readout collapse**
- not a complete collapse of the visual splice itself

## Evidence

### 1. Fixed tiny DN readout collapses by `500 ms`

From `outputs/metrics/splice_drift_audit_summary.json` under `hold`:

- fixed DN turn bias at `100 ms`
  - left condition: `-40`
  - right condition: `+100`
- fixed DN turn bias at `500 ms`
  - left condition: `0`
  - right condition: `0`

That means the original `DNa01/DNa02`-style turn readout no longer distinguishes left from right by `500 ms`.

### 2. Relay asymmetry persists under sustained input

Relay voltage contrast remains strong at `500 ms` for several groups:

- `LC31a`
  - contrastive right-minus-left:
    - `100 ms`: `+14.53`
    - `500 ms`: `+13.81`
- `LC31b`
  - contrastive right-minus-left:
    - `100 ms`: `+24.44`
    - `500 ms`: `+22.63`
- `LCe04`
  - contrastive right-minus-left:
    - `100 ms`: `+5.88`
    - `500 ms`: `+5.90`

So the relay stage is not where the sustained-input failure happens.

### 3. Broader descending groups still carry asymmetric rates at `500 ms`

Under `hold`, several strict descending/efferent groups remain asymmetric at `500 ms`:

- left condition:
  - `DNp09`: `-40`
  - `DNpe056`: `-80`
  - `DNp103`: `+160`
  - `DNg97`: `+80`
  - `DNp18`: `+120`
- right condition:
  - `DNp103`: `+40`
  - `DNpe040`: `+40`
  - `DNg97`: `-40`

So asymmetry is still reaching the descending layer; it is not only a relay-local effect.

### 4. There is no strong self-sustaining state after the input is removed

Under the `pulse_25ms` schedule:

- mean relay contrastive signal:
  - `100 ms`: about `0.0098`
  - `500 ms`: about `0.000055`
- mean descending contrastive signal:
  - `100 ms`: `0.0`
  - `500 ms`: `0.0`
- fixed DN turn bias:
  - `100 ms`: `0`
  - `500 ms`: `0`

So once the external splice input is removed, the asymmetry decays away almost completely.

That means the model, in its current public parameterization, does **not** show a robust self-maintaining visuomotor state after a short launch pulse.

## Mechanistic conclusion

The old `500 ms` sign collapse is best explained by **two distinct effects**:

1. `No persistent state after brief input`
- the current public whole-brain dynamics do not keep the launched asymmetry alive once the splice input is removed

2. `Fixed tiny DN readout collapses under sustained drive`
- with sustained input, relay and broader descending asymmetry remain present
- but the original tiny motor readout equalizes or becomes non-diagnostic by `500 ms`

So the remaining blocker is **not** “the splice dies everywhere by `500 ms`”.

It is narrower:

- the current fixed motor readout is too small / brittle for long-window interpretation
- and the current public recurrent dynamics do not maintain the state after a short pulse

## What this means for the project

1. The input splice is no longer the main long-window failure.
2. The fixed `DNa01/DNa02`-style motor readout is not sufficient as the only long-window motor interpretation layer.
3. The embodied descending-only branch remains the right direction, because it already widened the output side beyond that tiny DN bottleneck.
4. If long-window autonomous state matters, the next work should investigate:
   - recurrent normalization / state conditioning
   - or a richer motor readout than the original fixed DN set
