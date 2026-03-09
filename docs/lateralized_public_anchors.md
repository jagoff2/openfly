# Lateralized Public Anchors

This document records the search for truly lateralized public sensory anchors in the checked local public artifacts before attempting visually guided turning again.

## Reproduction

Run:

```bash
python scripts/search_lateralized_public_anchors.py
```

Artifact:

- `outputs/metrics/lateralized_public_anchors.json`

## Main Result

Within the checked public notebook artifacts under `external/fly-brain/code/paper-phil-drosophila`:

- no clearly lateralized visual anchor pool was found
- no clearly lateralized mechanosensory anchor pool was found
- only non-lateralized visual and mechanosensory pools were found
- lateralized sensory hits that do exist are gustatory, not visual or mechanosensory

## Evidence

### Visual

The public looming/vision example defines only:

- `external/fly-brain/code/paper-phil-drosophila/example.ipynb:367`

That cell defines `LC_4s`, with no public `LC4_left` or `LC4_right` counterpart in the checked notebook artifacts.

The search output reports:

- `visual_lateralized_hits = 0`
- `visual_non_lateralized_hits = 5`

### Mechanosensory

The public JO/JON material exposes:

- `external/fly-brain/code/paper-phil-drosophila/example.ipynb:441`
- `external/fly-brain/code/paper-phil-drosophila/example.ipynb:472`
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb:718`
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb:745`

These are functional subtype groups such as:

- `JO_EV`
- `JO_EDC`
- `JO_EDM`
- `JO_EDP`
- `JO_EVL`
- `JO_EVM`
- `JO_EVP`
- `JO_CA`
- `JO_CL`
- `JO_CM`
- `neu_JON_CE`
- `neu_JON_F`
- `neu_JON_D_m`

But the checked public artifacts do not expose left/right versions of those visual-turning-relevant mechanosensory pools.

The search output reports:

- `mechanosensory_lateralized_hits = 0`
- `mechanosensory_non_lateralized_hits = 22`

### Lateralized Sensory Hits That Do Exist

The search did find lateralized sensory examples, but they are gustatory:

- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb:59`
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb:469`
- `external/fly-brain/code/paper-phil-drosophila/figures.ipynb:1085`

So the checked public artifacts do contain lateralized sensory annotations in general, but not the visual or mechanosensory anchor pools needed for a clean left/right visual turning bridge here.

## Consequence For This Repo

The current strict production path should not pretend to have a public left/right visual steering signal when the checked public anchor pools do not provide one.

That means:

1. keep the bilateral public `LC4` / `JON` handling in place
2. do not reintroduce fabricated left/right sensory splits
3. do not claim visually guided turning from public anchors until a real public left/right sensory anchor set is identified

## Practical Next Step

If turning remains a priority, the next defensible step is:

- search beyond the currently checked notebook artifacts for additional public neuron-ID sources that explicitly annotate left/right visual or mechanosensory sensory populations

Until then, the repo can support:

- strict sensory-only mode with bilateral public anchors
- clearly labeled `public_p9_context` experiment mode

but not an honest claim of lateralized public visual steering input.
