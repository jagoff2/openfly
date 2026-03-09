# GitHub Upload Notes

This workspace was not originally a Git repository.

For GitHub publishing, the repo now excludes content that is either:

- re-creatable from scripts
- too large for a normal GitHub push
- duplicated generated runtime output

Excluded by `.gitignore`:

- `external/`
- `outputs/cache/`
- generated `*.jsonl`, `*.prof`, `*.pkl`, `*.parquet`, `*.feather`
- temporary test output under `tests/.tmp/`

Kept in the publishable repo:

- source code under `src/`
- configs, scripts, tests, benchmarks, docs
- root trackers and reports
- generated summary artifacts such as:
  - `outputs/benchmarks/`
  - `outputs/metrics/`
  - `outputs/plots/`
  - small demo videos and screenshots not filtered by `.gitignore`

Important implication:

- the pushed repo will still be reproducible from the checked-in scripts
- but the large downloaded public datasets and cache files will not be embedded in Git history

If you want the large artifacts online too, use one of:

1. GitHub Releases
2. Git LFS
3. an external artifact bucket
