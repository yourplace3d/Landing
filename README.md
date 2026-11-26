# The Your Place landing page

The page people see at [github.com/yourplace3d](https://github.com/yourplace3d): its text, its pictures
and the script that draws them.

## How it reaches the page

GitHub shows an organisation's page from `profile/README.md` in the repo named `.github`. That repo
copies this repo's `profile/` folder every hour, and on every run of its "Landing page" workflow
(`.github/workflows/landing.yml` there; a copy is in [`sync/landing.yml`](sync/landing.yml)).

So: change things here, and the page follows within the hour. To have it at once, open
[the workflow](https://github.com/yourplace3d/.github/actions) and press "Run workflow". GitHub
switches hourly runs off after 60 days without changes; "Run workflow" switches them on again.

## What is where

- `profile/README.md`: the page. Pictures are linked by their address in the `.github` repo, so they
  show there and here.
- `profile/assets/`: the pictures. Banner, flow and buttons are drawn by `tools/make.py`; the two
  screenshots come from the apps' own repos (1200 px wide, rounded corners, WebP).
- `tools/make.py`: draws the banner (light and dark), the five steps, the divider and the buttons:
  `python3 tools/make.py profile/assets`
- `tools/preview.py`: a local look-alike of the page, to check a change before it goes out
  (needs `pip install markdown`): `python3 tools/preview.py .`

The page is about the projects, not about a person: no names and no places of anyone on it.
