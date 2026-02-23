# IPTV Filter Auto Update

This repository keeps a filtered M3U playlist from:

- `https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u`

Only these `group-title` keywords are kept:

- `[三网]央卫视直播`
- `[联通]咪视界直播`

## Files

- `scripts/filter_playlist.py`: fetches source M3U and filters channels.
- `.github/workflows/update-playlist.yml`: runs daily and updates `playlist.m3u`.
- `playlist.m3u`: generated output file for subscription.

## Subscription URL

After pushing this repo to GitHub, use:

- `https://raw.githubusercontent.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPO>/main/playlist.m3u`

## Manual local run

```bash
python scripts/filter_playlist.py --output playlist.m3u
```

## Change schedule

Edit `.github/workflows/update-playlist.yml` cron:

- current: `15 0,12 * * *` (daily 00:15/12:15 UTC, i.e. 08:15/20:15 Beijing time)
