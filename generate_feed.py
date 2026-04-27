"""
Generates avfall-feed.rss with one item per collection week.
pubDate = Sunday 19:00 Oslo time before the collection week.
Run weekly via GitHub Actions on Sundays at 17:00 UTC = 19:00 CEST.
"""

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from collections import defaultdict

OSLO = timezone(timedelta(hours=2))  # CEST (summer time)

IKONER = {
    'Matavfall':                  '🥦',
    'Restavfall':                 '🗑️',
    'Plastemballasje':            '🧴',
    'Papir':                      '📰',
    'Glass- og metallemballasje': '🍾',
}

TYPE_ORDER = list(IKONER.keys())

ARTICLE_URL = 'https://www.horten.kommune.no/avfall-og-gjenvinning/nar-blir-avfallet-hentet/'

# All planned collection dates up to week 36.
# key = collection date (YYYY-MM-DD), value = list of waste types collected.
COLLECTIONS = {
    '2026-04-29': ['Matavfall', 'Plastemballasje'],
    '2026-05-06': ['Matavfall'],
    '2026-05-12': ['Matavfall', 'Restavfall'],
    '2026-05-18': ['Glass- og metallemballasje'],
    '2026-05-20': ['Papir'],
    '2026-05-27': ['Matavfall', 'Plastemballasje'],
    '2026-06-03': ['Matavfall'],
    '2026-06-10': ['Matavfall', 'Restavfall'],
    '2026-06-16': ['Papir'],
    '2026-06-17': ['Matavfall'],
    '2026-06-23': ['Plastemballasje'],
    '2026-06-24': ['Matavfall'],
    '2026-07-01': ['Matavfall'],
    '2026-07-07': ['Restavfall'],
    '2026-07-08': ['Matavfall'],
    '2026-07-13': ['Glass- og metallemballasje'],
    '2026-07-14': ['Papir'],
    '2026-07-21': ['Plastemballasje'],
    '2026-07-22': ['Matavfall'],
    '2026-07-29': ['Matavfall'],
    '2026-08-04': ['Restavfall'],
    '2026-08-05': ['Matavfall'],
    '2026-08-11': ['Papir'],
    '2026-08-12': ['Matavfall'],
    '2026-08-18': ['Plastemballasje'],
    '2026-08-19': ['Matavfall'],
    '2026-08-26': ['Matavfall'],
}


def group_by_week():
    """Groups all collection types by ISO (year, week), sorted consistently."""
    weeks = defaultdict(set)
    for date_str, typer in COLLECTIONS.items():
        d = datetime.strptime(date_str, '%Y-%m-%d')
        iso_year, iso_week, _ = d.isocalendar()
        weeks[(iso_year, iso_week)].update(typer)
    return {
        k: sorted(v, key=lambda t: TYPE_ORDER.index(t) if t in TYPE_ORDER else 99)
        for k, v in sorted(weeks.items())
    }


def sunday_pub_dt(iso_year, iso_week):
    """Returns Sunday 19:00 Oslo time before the given ISO week starts."""
    monday = datetime.strptime(f'{iso_year}-W{iso_week:02d}-1', '%G-W%V-%u')
    sunday = monday - timedelta(days=1)
    return datetime(sunday.year, sunday.month, sunday.day, 19, 0, 0, tzinfo=OSLO)


def typer_streng(typer):
    if len(typer) == 1:
        return typer[0]
    return ', '.join(typer[:-1]) + ' og ' + typer[-1]


def build_feed(items_xml, now_str):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Avfallshenting i Horten</title>
    <link>{ARTICLE_URL}</link>
    <description>Ukentlige varsler om avfallshenting i Horten kommune.</description>
    <lastBuildDate>{now_str}</lastBuildDate>
    <atom:link href="https://edrenate.github.io/horten-renovasjon-widget/avfall-feed.rss" rel="self" type="application/rss+xml"/>
    <managingEditor>post@horten.kommune.no (Horten kommune)</managingEditor>
    <ttl>60</ttl>{items_xml}
  </channel>
</rss>"""


def main():
    now = datetime.now(tz=OSLO)
    weeks = group_by_week()
    items_xml = ''

    for (iso_year, iso_week), typer in weeks.items():
        pub_dt = sunday_pub_dt(iso_year, iso_week)

        if pub_dt > now:
            continue

        ikoner = ' '.join(IKONER.get(t, '♻️') for t in typer)
        ts = typer_streng(typer)

        title = f'{ikoner} Avfallshenting denne uka – {ts}'
        desc = (
            f'Denne uka (uke {iso_week}) hentes følgende avfall i Horten: {ts}. '
            f'Sjekk hvilken dag avfallet hentes hos deg på horten.kommune.no.'
        )

        items_xml += f"""
    <item>
      <title>{title}</title>
      <description>{desc}</description>
      <pubDate>{format_datetime(pub_dt)}</pubDate>
      <guid isPermaLink="false">horten-avfall-uke-{iso_year}-{iso_week:02d}</guid>
      <link>{ARTICLE_URL}</link>
    </item>"""

    feed = build_feed(items_xml, format_datetime(now))

    with open('avfall-feed.rss', 'w', encoding='utf-8') as f:
        f.write(feed)

    print(f'Feed generert: {items_xml.count("<item>")} items (per {now.strftime("%Y-%m-%d %H:%M %Z")})')


if __name__ == '__main__':
    main()
