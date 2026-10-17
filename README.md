# CBA Pinterest feeds
Releases 8 pins a day from `pins.json` into one RSS feed per Pinterest board (`feeds/`).
Pinterest auto-publishes new items from each feed (Pinterest > Settings > Bulk create Pins > RSS feed).
- Change pace: edit `per_day` in `config.json`.
- Add pins: append to `pins.json` (title, image, board, description, link).
