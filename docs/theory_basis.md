# Theory Basis for HydroResKit

HydroResKit needs theory support, but it should not become a theory paper. The theory is used to constrain the indicator schema and make the computation auditable.

## Why Theory Is Needed

Without theory, the toolkit would look like a collection of convenient variables. The resilience schema answers three questions:

- what disturbance or stress is being represented;
- what system elements are exposed and sensitive;
- what capacity or recovery signal can reduce or absorb adverse impacts.

This is the difference between a reusable scientific workflow and a set of scripts.

## Minimal Theoretical Anchors

HydroResKit should use two anchors:

- IPCC climate-risk framing: risk emerges from interactions among hazard, exposure, and vulnerability. Vulnerability includes sensitivity and lack of capacity to cope and adapt.
- Social-ecological resilience: a basin is treated as a coupled human-water-ecosystem unit whose capacity to absorb disturbance, adapt, and recover can be represented through measurable proxies.

Letter-ready sentence:

> HydroResKit is grounded in the IPCC climate-risk framing of hazard, exposure, and vulnerability, and further incorporates adaptive capacity and recovery from social-ecological resilience thinking.

## Mapping to the HydroResKit Schema

| HydroResKit dimension | Theoretical role | Example indicators |
|---|---|---|
| hazard | climate or hydrological stressor | extreme precipitation, drought intensity, flood-prone terrain |
| exposure | people, assets, land systems, or activities in affected places | population density, built-up fraction, cropland fraction |
| sensitivity | propensity of the exposed system to be adversely affected | slope, impervious fraction, ecological fragility, water-stress proxy |
| adaptive_capacity | capacity to cope, buffer, or adapt | surface water fraction, green-blue space, socioeconomic proxy |
| recovery | observed return or rebound after stress | NDVI recovery, water occurrence recovery, night-light recovery |

## How to Use Theory in the FCS Letter

Use theory only in three places:

- one short paragraph in the introduction;
- a schema explanation in the implementation section;
- an indicator table in the supplementary materials.

Do not make claims such as:

- "HydroResKit proves the resilience mechanism of the Yangtze River Basin."
- "The selected indicators fully represent watershed resilience."

Use cautious claims:

- "HydroResKit operationalizes a transparent indicator schema for watershed climate-resilience assessment."
- "The schema can be modified by users, while provenance records preserve the assumptions behind each indicator."
