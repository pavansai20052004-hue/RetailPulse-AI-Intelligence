# RetailPulse Deployment

RetailPulse is deployed as a single Streamlit web service. The application is
stateless and reads the checked-in processed dataset at
`data/processed/cleaned_online_retail.csv`.

## Deployment contents

The Docker image contains only:

- `app/`
- `src/`
- `data/processed/`
- `requirements.txt`, `pyproject.toml`, and `README.md`

The raw workbook, notebooks, tests, generated output, reports, caches, local
environments, and Streamlit secrets are excluded from the Docker build context.
No persistent disk or external database is required.

Before deployment, confirm that
`data/processed/cleaned_online_retail.csv` is committed to the repository. The
dashboard cannot rebuild it in production because `data/raw/online_retail.xlsx`
is intentionally excluded.

## Local Python run

Python 3.12 is the supported runtime.

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
streamlit run app/dashboard.py
```

Verify readiness at:

```text
http://localhost:8501/_stcore/health
```

## Local Docker run

```bash
docker build --tag retailpulse:local .
docker run --rm --name retailpulse -p 8501:8501 retailpulse:local
```

Then open `http://localhost:8501` and verify:

```bash
curl --fail http://localhost:8501/_stcore/health
```

The Dockerfile defaults to port `8501`. Render overrides the container command
and binds Streamlit to Render's injected `PORT` value.

## Render deployment

The root `render.yaml` defines a Docker web service with:

- A Starter instance.
- Automatic deployment on commits to the linked branch.
- Binding to `0.0.0.0:$PORT`.
- Streamlit's `/_stcore/health` readiness endpoint.
- Production-safe Streamlit error, toolbar, telemetry, and file-watcher
  settings.

To deploy:

1. Push the repository, including the processed CSV, to a supported Git
   provider.
2. In Render, create a new Blueprint and select the repository.
3. Review the service name, region, and Starter instance cost.
4. Apply the Blueprint and wait for the health check to pass.
5. Open the generated `onrender.com` URL and exercise every dashboard tab.

No environment variables or secrets are currently required. Do not add a
`PORT` variable manually; Render provides it.

## Capacity guidance

The processed CSV is approximately 37 MiB and expands substantially in memory
after Pandas parsing and feature enrichment. Each active filter context also
runs forecasting, K-Means clustering, churn modeling, and inventory analysis.
The Blueprint therefore uses `starter` instead of `free`.

Monitor memory, CPU, startup time, and request latency after deployment. Move to
a larger instance if Render reports out-of-memory restarts or if concurrent
sessions make model execution unresponsive.

## Release verification

Run these checks before a release:

```bash
python -m pip check
python -m pytest -q
python -c "from retailpulse.data import load_dataset; df = load_dataset(); print(len(df), df.shape[1])"
```

For a container release, also build the image and confirm both `/` and
`/_stcore/health` respond successfully. A Render deploy is complete only after
the service health check passes and the processed dataset loads without a
missing-file error.

