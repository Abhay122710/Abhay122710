# Profile card maintenance

The profile uses self-contained SVG images with embedded, subset Kanit fonts
(SIL Open Font License in `fonts/OFL.txt`) and the existing profile portrait.
Every card supports reduced motion. No external font or statistics service is
required to display the README.

## Refresh

```sh
python3 scripts/render_readme_cards.py --refresh
```

Python 3.10+; standard library only. The public GitHub contribution calendar is
saved to `data/contributions.json`. Exact tooltip counts are parsed and validated;
an incomplete or changed upstream format fails before replacing the last snapshot.
Counts reflect GitHub's public calendar and can include anonymous private activity
if enabled in your GitHub profile settings. No private repository names are read.

The GitHub Action runs daily at 01:17 UTC (06:47 India time), on relevant source
changes, and from **Actions → Refresh profile cards → Run workflow**. Scheduled
runs can be delayed by GitHub. GitHub may disable schedules after prolonged
inactivity in public repositories; re-enable from Actions if needed.

## Preview and personalize

```sh
STATIC=1 OUTPUT_DIR=/tmp/profile-static python3 scripts/render_readme_cards.py
```

`STATIC=1` renders the final frame without animation. Normal renders use CSS
entrances, growing bars, pulsing dots, and nudging arrows. All motion stops under
`prefers-reduced-motion: reduce`; SVGs have accessible titles/descriptions and
README images have alternate text.

Edit text, colors, and project cards in `scripts/render_readme_cards.py`. Edit
click destinations and text alternatives in `README.md`, then render again.
The current streak includes today when active, otherwise ends yesterday. Longest
streak and active days cover the fetched calendar window; monthly edge buckets
can be partial. Dates follow GitHub's UTC calendar, not the viewer's local date.

The daily refresh itself may count as GitHub activity. Counts are activity
indicators, not measures of skill or code quality.

Design inspired by Avi Vashishta's animated SVG README article; implementation,
layout and personal content are original to this profile.
