# Inferred Lateralized Visual Candidates

This document records the first inference pass for left/right visual bridge candidates. It is weaker evidence than the public notebook anchors in `docs/lateralized_public_anchors.md`.

## Method

- Run the real FlyVis network with crafted grayscale stimuli:
  - `baseline_gray`
  - `body_left_dark`
  - `body_center_dark`
  - `body_right_dark`
- Average the trailing network responses for every valid visual cell type.
- Rank cell types by whether their left-eye minus right-eye response flips sign when the dark patch moves from the fly's left field to the fly's right field.

Code and artifacts:
- `scripts/probe_lateralized_visual_candidates.py`
- `src/vision/lateralized_probe.py`
- `outputs/metrics/inferred_lateralized_visual_candidates.csv`
- `outputs/metrics/inferred_lateralized_visual_candidates.json`
- `outputs/metrics/inferred_lateralized_visual_recommended.json`
- `outputs/plots/inferred_lateralized_visual_stimuli.png`

## Main Findings

- The probe found strong mirror-consistent left/right selectivity in several visual cell types.
- The strongest inferred tracking candidates were:
  - `TmY14`
  - `TmY15`
  - `TmY5a`
  - `TmY4`
  - `TmY18`
  - `TmY9`
- The strongest inferred flow candidates were:
  - `T5d`
  - `T5c`
  - `T4b`
  - `T5a`

## What This Means

- The current repo was not missing the relevant FlyVis cell families entirely.
- Most top inferred candidates are already in the production tracking/flow cell lists in `src/brain/public_ids.py`.
- The current blocker is that the production extractor averages those cells into bilateral salience and bilateral flow summaries, then the brain backend collapses the public sensory input back to bilateral `LC4` / `JON` pools.
- In other words: the current bridge already looks at many of the right visual cells, but it throws away the lateralized sign structure that the probe recovered.

## Reusable Experimental Output

The repo now includes a reusable experimental loader and turn-bias extractor:

- `src/vision/inferred_lateralized.py`
- `tests/test_inferred_lateralized.py`

This code:
- loads the ranked probe artifact
- keeps the top sign-flipping tracking and flow candidates
- assigns each candidate a polarity based on which eye leads for a right-side stimulus
- computes an experimental `turn_bias` from live per-eye activity arrays

This remains experimental. It does not yet change the production bridge or claim a faithful biological mapping into the whole-brain backend.

## Current Boundary

What this inference does give us:
- a defensible experimental left/right visual signal derived from the real FlyVis network

What it still does not give us:
- a public-grounded whole-brain neuron-ID mapping for those left/right visual signals
- a faithful default bridge from inferred visual candidates into locomotor descending neurons

That next step remains an explicitly inferred experiment, not a public-grounded parity claim.
