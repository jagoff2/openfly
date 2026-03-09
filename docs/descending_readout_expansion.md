## Descending-Only Readout Expansion

Ground truth for this branch is the user correction that optic-lobe or visual relay neurons must not be treated as final motor outputs. This document records the replacement branch that mines only public descending/efferent candidates, selects a broader descending-only readout, and tests it with the existing embodied visual splice and no body fallback.

### Why this branch exists

The earlier embodied splice run at `outputs/requested_2s_splice/flygym-demo-20260309-100707` proved that the new visual splice reaches the brain and produces commands, but it did not produce useful locomotion:

- `avg_forward_speed = 1.0916253476635753`
- `path_length = 2.1810674446318234`
- `net_displacement = 0.11315538386569819`
- `displacement_efficiency = 0.05188073580402254`

The follow-up audit in `TASKS.md:T067` showed that the visual splice was active on almost every cycle, but the output side remained bottlenecked by the tiny fixed descending readout set in `src/brain/public_ids.py`.

The invalid relay-expanded branch was explicitly abandoned because it treated optic-lobe / visual relay classes as motor outputs, which is biologically wrong.

### Public descending candidate mining

I replaced the invalid relay-expanded branch with a strict descending-only mining step:

- script: `scripts/find_descending_readout_candidates.py`
- outputs:
  - `outputs/metrics/descending_readout_candidates_strict.json`
  - `outputs/metrics/descending_readout_candidates_strict_pairs.csv`
  - `outputs/metrics/descending_readout_candidates_strict_roots.csv`

The strict filter is:

- `super_class == descending`
- `flow == efferent`
- label matches `DN*`, `oDN*`, or `MDN*`

This explicitly excludes the previously tempting but wrong `cL22*` / `VES015` / `VES026` visual-centrifugal cells.

Top strict descending bilateral candidates by structural input from the splice relay layer:

- `DNp09` / pair score `1166.0`
- `DNp35` / pair score `617.0`
- `DNp06` / pair score `592.0`
- `DNpe031` / pair score `542.0`
- `DNb01` / pair score `519.0`
- `DNp71` / pair score `398.0`
- `DNb09` / pair score `371.0`
- `DNp103` / pair score `365.0`
- `DNp43` / pair score `327.0`
- `DNg97` / pair score `325.0`
- `DNp18` / pair score `320.0`
- `DNpe056` / pair score `290.0`
- `DNae002` / pair score `280.0`
- `DNpe040` / pair score `265.0`
- `DNpe016` / pair score `260.0`
- `DNp69` / pair score `215.0`

### Body-free descending probe

I then probed those descending candidates without the body loop:

- script: `scripts/run_descending_readout_probe.py`
- outputs:
  - `outputs/metrics/descending_readout_probe_strict.csv`
  - `outputs/metrics/descending_readout_probe_strict_pairs.csv`
  - `outputs/metrics/descending_readout_probe_strict_summary.json`

The probe used the already calibrated splice settings:

- signed direct current
- `axis1d`
- `4` bins
- the exact shared `cell_type + side + bin` boundary

Important interpretation:

- the `500 ms` probe window is not trustworthy as a selector because `T062` already showed recurrent downstream drift at longer windows
- the `100 ms` probe window is therefore the selection window for the expanded descending readout

### Selection rule for supplemental descending readout groups

The current decoder still keeps the original fixed DN readout set:

- `DNp09` / `P9`
- `DNg97` / `oDN1`
- `DNa01`
- `DNa02`
- `MDN`

The supplemental branch should therefore add broader descending evidence without simply duplicating the same tiny fixed set.

I encoded the selection step in:

- `scripts/select_descending_readout_groups.py`
- output: `outputs/metrics/descending_readout_recommended.json`

Selection rule:

- forward-support groups:
  - high bilateral firing at `100 ms`
  - low left/right imbalance
- turn-support groups:
  - explicit rate-level sign flip between left-dark and right-dark conditions at `100 ms`
- excluded from supplemental lists because they are already part of the fixed decoder DN set:
  - `DNp09`
  - `DNg97`
  - `DNa02`

Recommended supplemental forward groups:

- `DNp103`
- `DNp06`
- `DNp18`
- `DNp35`

Recommended supplemental turn groups:

- `DNpe056`
- `DNp71`
- `DNpe040`

### Physical location of the selected groups

All selected supplemental groups are public `descending` + `efferent` annotations in the supplement. They are not optic-lobe relay classes.

Mean soma coordinates from `outputs/metrics/descending_readout_candidates_strict.json`:

- `DNp35`
  - left soma `106488, 51472, 5322`
  - right soma `156416, 50800, 4935`
- `DNp06`
  - left soma `107216, 50288, 5411`
  - right soma `156616, 52472, 5064`
- `DNp71`
  - left soma `108408, 49192, 5307`
  - right soma `156704, 48680, 4866`
- `DNp103`
  - left soma `107304, 55320, 5479`
  - right soma `160192, 60856, 5042`
- `DNp18`
  - left soma `113488, 47432, 5295`
  - right soma `153768, 52048, 5053`
- `DNpe056`
  - left soma `110984, 47144, 5348`
  - right soma `153008, 46320, 5022`
- `DNpe040`
  - left soma `117576, 48712, 5538`
  - right soma `149624, 45032, 5101`

This is the anatomically correct side of the system for a motor readout experiment: descending/efferent outputs rather than visual relay classes.

### Embodied descending-only test

I wired the selected groups into a new embodied config:

- `configs/flygym_realistic_vision_splice_axis1d_descending_readout.yaml`

The embodied run used:

- the new visual splice from `configs/flygym_realistic_vision_splice_axis1d.yaml`
- no `P9` prosthetic brain context
- no optic-lobe-as-motor shortcut
- no decoder idle-drive fallback
- no body-side locomotion fallback

Artifacts:

- benchmark: `outputs/benchmarks/fullstack_splice_descending_2s.csv`
- plot: `outputs/plots/fullstack_splice_descending_2s.png`
- video: `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/demo.mp4`
- log: `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/run.jsonl`
- metrics: `outputs/requested_2s_splice_descending/flygym-demo-20260309-115041/metrics.csv`

Result:

- `sim_seconds = 2.0`
- `avg_forward_speed = 4.563790532043783`
- `path_length = 9.11845348302348`
- `net_displacement = 5.633006914226428`
- `displacement_efficiency = 0.6177590229213569`
- `stable = 1.0`
- `real_time_factor = 0.0024065159023714164`

Comparison against the previous splice-only embodied run:

- artifact: `outputs/metrics/descending_readout_comparison.csv`
- artifact: `outputs/metrics/descending_readout_comparison.json`

Key improvement:

- old splice-only `net_displacement = 0.11315538386569819`
- descending-readout `net_displacement = 5.633006914226428`

- old splice-only `displacement_efficiency = 0.05188073580402254`
- descending-readout `displacement_efficiency = 0.6177590229213569`

- old splice-only mean drives:
  - left `0.04576752944365208`
  - right `0.038295875266585365`
- descending-readout mean drives:
  - left `0.31380241125955`
  - right `0.19510758948955362`

### What this does and does not prove

What it proves:

- the current embodied failure was not just an input-splice problem
- a broader, descending-only readout materially improves actual movement without using optic-lobe neurons as motor outputs
- the visual splice plus whole-brain dynamics can now produce meaningful traversal in the body loop with no `P9` prosthetic mode

What it does not prove:

- that this is the final biologically correct descending readout
- that the locomotor policy is behaviorally correct in detail
- that the missing VNC / premotor structure has been solved

This branch is a grounded improvement, not a final biological victory claim.
