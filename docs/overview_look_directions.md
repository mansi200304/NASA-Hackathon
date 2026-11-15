# Overview text: why we look from two sides

**Draft for the Overview page. Not on the website yet.** Add it once the Overview page is merged. Plain language (about US grade 7); no numbers that will go stale except where marked.

---

## Two ways of looking

A radar satellite does not look straight down. It looks at the ground from the side, at a slant, and it can only measure how far the ground moves **toward or away from that slanted view**.

Satellites circle the Earth in two directions, so the same patch of ground gets measured from two sides:

- **Heading south**, the satellite looks toward the west.
- **Heading north**, the satellite looks toward the east.

## Why we use both

**It is a check that does not depend on luck.** Many errors belong to one view only: moisture in the air on one day, a mountain shadow, an unlucky reference point. They do not repeat from the other side. When both views show sinking in the same place, it is very unlikely to be an error.

**It tells us the ground is mostly going down, not sideways.** Ground that sinks straight down moves *away* from both views. Sideways motion would look different from each side: closer from one, farther from the other.

## What the labels on the map mean

- **Both look directions.** The second view also shows sinking over the same ground.
- **Unconfirmed, single look direction.** Only one view covers this area, so we could not cross-check it ourselves. That does not mean it is wrong. For Bowie–San Simon, Arizona's water agency (ADWR) measures the same pattern with a separate satellite.

## What we still do not know

The two views agree on **where** the ground is sinking and roughly **how much**, but not exactly. In three of our four cross-checked areas (Willcox, Fort Grant Road, Elfrida), the second view reads about a quarter to a third smaller. At Eloy, which is a small patch, it reads a little larger instead. The cause could be the different viewing angles, some sideways motion, or the choice of reference ground. We have not pinned it down. The size of that disagreement is included in the "give or take" shown with each rate.

In principle, two views can be combined to separate up-and-down motion from east-west motion. We have not done that: it needs both views over the same period, and our second view has fewer dates.

---

## Short versions (for hover text next to the labels)

- **Both look directions:** "Satellite views from both the east and the west show sinking here."
- **Single look direction:** "Only one viewing direction covers this area, so we could not cross-check it ourselves."

## Where the data lives

Each study's label comes from `confirmation` in `data/processed/hotspots.geojson` (`both look directions`, `single look direction`, or `weak in second direction`). The two medians behind it are in `timeseries_<slug>.json` (`median_rate_cm_yr` and `ascending_check`). If the text above quotes percentages, regenerate them from those fields.
