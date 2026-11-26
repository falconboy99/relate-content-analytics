# Relate — Content Intelligence

[![CI](https://github.com/falconboy99/relate-content-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/falconboy99/relate-content-analytics/actions/workflows/ci.yml)

A complete Data-Driven Social Engagement Initiative project built around **Seen & Understood**, an original content series. Includes a responsive analytics dashboard, cleaned datasets, a portable NLP model, statistical comparisons, a strategy report and creative deliverables.

**All bundled campaign data is synthetic.** No social accounts were accessed and no engagement results are real. Import your own campaign exports when real data is available.

## Open the dashboard

```sh
git clone https://github.com/falconboy99/relate-content-analytics.git
cd relate-content-analytics
npm run build
npm start
```

Visit **http://127.0.0.1:5174**. Node.js 22+ and Python 3.10+; no npm dependencies. Do not open index.html as a file URL.

## Deploy

Upload the contents of `dist/` to a static web host. `index.html` must sit at the site root. Or configure a host to run `npm run build` with publish directory `dist`. No secrets or environment variables required. Hash navigation works without routing rewrites. See `reports/deployment.html`.

## Five deliverables

1. **Dashboard:** `src/` source and `dist/` deployable build. Overview, content library, sentiment, experiments, strategy/trends, and data import/export. Filters, searchable tables, post inspection, local NLP inference, CSV/JSON import, exports, responsive layouts.
2. **Structured dataset:** `data/raw/`, `data/clean/`, `data/templates/`. 24 cleaned posts, 720 comments, 36 weekly trend records; raw duplicates retained for audit. Data dictionary: `reports/methodology.html`.
3. **NLP model:** `python/sentiment.py`, `models/sentiment.json`, `models/evaluation.json`, and `data/sentiment_corpus.csv`. Naive Bayes, word unigrams/bigrams, author-labeled 120-row training set and 36-row held-out set. 88.9% holdout accuracy; not a real-world benchmark.
4. **Strategy report:** `reports/strategy-report.pdf`. Findings, metrics, limitations, matched hook test and next campaign plan. `reports/analysis.json` contains reproducible underlying results.
5. **Content series:** 12 original 1080×1350 ready-to-post PNG cards in `content/png/` and editable SVG social cards in `content/`; complete scripts, captions and A/B hooks in `content/series.json` and `reports/content-series.pdf`. Cards are finished assets; videos are scripts ready for filming, not produced video files.

## Real-data workflow

Export posts at a consistent observation age and comments with stable IDs. Map fields to the supplied template headers. Never fill unavailable metrics with zero. Import both CSVs in Data Studio, with optional trends, or run:

```sh
python3 python/pipeline.py --input /path/to/exports --output data/clean --source user_import
npm run build
```

The importer is atomic: invalid records leave the previous campaign intact. Identical IDs are deduplicated; conflicting IDs and orphan comments fail. The browser reclassifies comments with the bundled model and keeps imports in memory. Export Full JSON before refreshing. **No live social API integration or scheduled collection is connected.** A file-based ingestion pipeline is provided.

Files bundled in a public static deployment are public. Use anonymized data or the demo. Browser imports are local and never uploaded. Static PDF reports continue to describe the demo; Strategy's **Export this analysis** uses the current filtered campaign.

## NLP CLI

```sh
python3 python/sentiment.py --text "I thought I was the only one"
python3 python/sentiment.py --input comments.csv --output tagged.csv
python3 python/sentiment.py --train
```

`--input` requires a `text` column. The model tags **Relatable** or **Neutral**, adds an uncalibrated Relatable score, review flag and influential features. English only; review negation, sarcasm and multilingual content. Holdout mistakes are preserved.

## Reproduce the demo and reports

```sh
python3 python/create_corpus.py
python3 python/sentiment.py --train
python3 python/generate_demo.py
python3 python/pipeline.py --source synthetic_demo
node python/analysis.mjs
python3 -m pip install -r requirements-reports.txt
python3 python/make_reports.py
python3 python/make_docs.py
npm test
npm run build
python3 python/package_project.py
```

Only PDF generation requires ReportLab. Core inference, CSV cleaning, testing and dashboard operation require no third-party packages. Preserve real exports before running the demo generator.

## Analytical scope

- Growth is post-attributed gains, not net follower change.
- Reach is summed post reach, not unique campaign users.
- Viral score is `100 × (3 shares + 2 saves + likes) / reach`, a descriptive proxy, not a learned virality probability.
- Topic rankings use predicted labels in sampled comments. Wilson intervals omit model error and clustering.
- A/B analysis uses complete matched content pairs and a two-sided sign-flip permutation test. Organic comparisons are observational.
- Trends use a linear seven-day extrapolation and a held-last-point error diagnostic. Inputs are simulated in the demo.
- Length, caption and posting-time effects are not identifiable from this demo and are presented as future experiments.

The browser implementation is a portable alternative to the Power BI/Tableau/Streamlit options described in the brief. SQL schema is provided in `data/schema.sql` for moving the clean data into a database later.

The supplied PNG cards are pre-rendered. Optional regeneration: install Sharp, then run `node python/render_cards.mjs`. This is not required for the dashboard or normal builds.

## Repository quality checks

Run `npm run check` to execute the JavaScript/Python tests, recreate `dist/`, and verify all deployed assets against their source. GitHub CI runs the same checks on pushes to `main` and pull requests, checks that the committed build is current, and produces a downloadable deliverables artifact. Actions are pinned to verified commit SHAs and run with read-only repository permissions.

`dist/` is a disposable build directory and is recreated on each build. Keep real source exports in `data/` or outside the repository. Generated ZIPs, caches, local environments and secrets are ignored. The committed `dist/` is included for direct static hosting.

## Deploy from this repository

For a static hosting provider, select this repository, leave the project root at the repository root, set **build command** to `npm run build` and **publish directory** to `dist`. No environment variables are required. `netlify.toml` already contains these settings. Hosting is not automatically enabled by pushing the repository.

For **Vercel**, import this repository with **Root Directory** set to the repository root (`.`). The committed `vercel.json` selects the **Other** framework preset, runs `npm run build`, and serves `dist/`. Installation is skipped because the dashboard has no npm dependencies. Node.js is pinned to 22.x to match CI. Do not use `npm start` as the build command: it starts a local preview server. Deploy the latest commit after changing settings; redeploying an older commit will not include the new configuration.

- [Deployment guide](reports/deployment.html)
- [Methodology and data dictionary](reports/methodology.html)
- [Strategy report (PDF)](reports/strategy-report.pdf)
- [Content playbook (PDF)](reports/content-series.pdf)
- [Validation record](reports/validation.html)

## Example creative assets

<img src="content/png/C01.png" width="220" alt="Still replaying that one sentence? Social anxiety concept."> <img src="content/png/C03.png" width="220" alt="You do not have to earn a quiet evening. Burnout concept.">
