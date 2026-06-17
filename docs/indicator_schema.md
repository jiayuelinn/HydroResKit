# Indicator Schema

HydroResKit organizes indicators into five dimensions:

- hazard
- exposure
- sensitivity
- adaptive_capacity
- recovery

Every indicator entry must define:

- indicator ID;
- dimension;
- variable name;
- source dataset;
- spatial and temporal resolution;
- expected direction;
- aggregation method;
- missing-value rule;
- uncertainty note;
- citation.

The schema is stored in `configs/indicator_schema.yml`.

