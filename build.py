"""Builds one RSS feed per Pinterest board, releasing `per_day` more pins each day from pins.json.
Run daily by .github/workflows/daily.yml. Pinterest auto-publishes new feed items (Settings > Bulk create Pins > RSS)."""
import json, re, datetime as dt, html, os
from email.utils import format_datetime
cfg = json.load(open('config.json'))
pins = json.load(open('pins.json'))
today = dt.date.today()
start = dt.date.fromisoformat(cfg['start_date'])
days = (today - start).days
released = [] if days < 0 else pins[: cfg.get('first_day', cfg['per_day']) + cfg['per_day'] * days]
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower().replace('&', 'and')).strip('-')
boards = {}
for i, p in enumerate(pins):
    boards.setdefault(p['board'], [])
for i, p in enumerate(released):
    fd = cfg.get('first_day', cfg['per_day']); day = start + dt.timedelta(days=0 if i < fd else 1 + (i - fd) // cfg['per_day'])
    p = dict(p, idx=i, date=dt.datetime(day.year, day.month, day.day, 7, 0, i % cfg['per_day'], tzinfo=dt.timezone.utc))
    boards[p['board']].append(p)
os.makedirs('feeds', exist_ok=True)
links = []
seen_links = {}
for board, items in boards.items():
    s = slug(board)
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">', '<channel>',
           f'<title>{html.escape(cfg["site_title"] + " - " + board)}</title>', f'<link>{cfg["shop_url"]}</link>',
           f'<description>{html.escape(board)}</description>']
    for p in items:
        n = seen_links.get(p['link'], 0) + 1; seen_links[p['link']] = n
        link = p['link'] + ('?utm_source=pinterest&utm_content=pin%d' % n)
        img = p['image']
        desc = f'<p><img src="{img}" alt="{html.escape(p["title"])}"/></p><p>{html.escape(p["description"])}</p>'
        out += ['<item>', f'<title>{html.escape(p["title"])}</title>', f'<link>{html.escape(link)}</link>',
                f'<guid isPermaLink="false">cba-pin-{p["idx"]}</guid>', f'<pubDate>{format_datetime(p["date"])}</pubDate>',
                f'<description><![CDATA[{desc}]]></description>',
                f'<enclosure url="{html.escape(img)}" type="image/jpeg" length="0"/>',
                f'<media:content url="{html.escape(img)}" medium="image" type="image/jpeg"/>', '</item>']
    out += ['</channel>', '</rss>']
    open(f'feeds/{s}.xml', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    links.append((board, s, len(items)))
rows = ''.join(f'<tr><td>{html.escape(b)}</td><td><a href="feeds/{s}.xml">feeds/{s}.xml</a></td><td>{n}</td></tr>' for b, s, n in sorted(links))
open('index.html', 'w', encoding='utf-8').write(
    f'<!doctype html><meta charset="utf-8"><title>CBA Pinterest feeds</title>'
    f'<style>body{{font:15px system-ui;margin:24px;color:#3c2828;background:#f7f0e7}}td{{padding:4px 12px}}</style>'
    f'<h1>CBA Pinterest feeds</h1><p>{len(released)} of {len(pins)} pins released (updated {today}).</p>'
    f'<table><tr><th>Board</th><th>Feed</th><th>Pins</th></tr>{rows}</table>')
print(f'{len(released)}/{len(pins)} released')
