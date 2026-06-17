# Installation

HydroResKit can be installed in editable mode during development:

```bash
python -m pip install -e .
```

For geospatial workflows, install the optional geospatial dependencies:

```bash
python -m pip install -e ".[geo]"
```

For development and tests:

```bash
python -m pip install -e ".[geo,dev]"
```

## Conda Environment

An example Conda environment is provided in `environment.yml`:

```bash
conda env create -f environment.yml
conda activate hydroreskit
python -m pip install -e .
```

## Quick Validation

```bash
python -m hydroreskit.cli validate-schema configs/indicator_schema.yml
python -m hydroreskit.cli demo configs/yangtze_demo.yml
python scripts/build_static_indicator_table.py configs/yangtze_static_sources.yml
python -m hydroreskit.cli demo configs/yangtze_static_demo.yml
```

Raw third-party data are not included in the repository. See `docs/data_sources.md` and `docs/release_data_policy.md` for data acquisition boundaries.
