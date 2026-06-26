# Changelog

## 0.1.0

- Initial release: versioned golden-dataset loader, LLM-as-judge (robust median
  + pairwise position-swap), mean/stdev/pass-rate metrics, and a CI regression
  gate that fails the build on a quality drop.
- Bootstrap confidence intervals on the mean (`bootstrap_ci`, deterministic via
  seed); surfaced in `ScoreStats` and the CLI.
- Provider middleware (`cache.py`): `CachingProvider` plus
  `MeteredProvider` / `UsageMeter` to cache repeated judge prompts and report
  tokens / cost / latency; enabled with the `--cache` CLI flag.
- More forgiving judge JSON parsing (handles fenced or prose-wrapped output).

## [Unreleased]

### Added
- `similarity.py`: reference-based metrics (exact match, token-F1, cosine, keyword recall).
- `calibration.py`: judge-vs-human calibration (Cohen's / weighted kappa, Pearson/Spearman correlation, MAE, and false-positive/negative rates at a pass threshold).
- OpenRouter provider option for the judge (`--provider openrouter`).
