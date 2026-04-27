"""
Generates avfall-feed.xml with only items whose pubDate has been reached.
Run daily via GitHub Actions. The RSS monitor in the app will detect
each new item (by guid) and trigger a push notification.
"""

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

OSLO = timezone(timedelta(hours=2))  # CEST (summer time)

UKEDAG = ['mandag','tirsdag','onsdag','torsdag','fredag','lørdag','søndag']
MAANED = ['januar','februar','mars','april','mai','juni','juli','august',
          'september','oktober','november','desember']

IKONER = {
    'Matavfall':                  '🥦',
    'Restavfall':                 '🗑️',
    'Plastemballasje':            '🧴',
    'Papir':                      '📰',
    'Glass- og metallemballasje': '🍾',
}

# Link users to the widget article where they can look up their own address.
# Update this URL when the article is published on the final page.
ARTICLE_URL = 'https://www.horten.kommune.no/renovasjon/hentedager-for-avfall/'

# All planned collection dates up to week 36.
# key = collection date (YYYY-MM-DD), value = list of waste types collected.
# pubDate = 07:00 Oslo time the DAY BEFORE collection.
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


def pub_datetime(collection_date_str):
    """Returns 07:00 Oslo time the day before the collection date."""
    d = datetime.strptime(collection_date_str, '%Y-%m-%d')
    dag_foer = d - timedelta(days=1)
    return datetime(dag_foer.year, dag_foer.month, dag_foer.day, 7, 0, 0,
                    tzinfo=OSLO)


def norsk_dato(d):
    return f'{UKEDAG[d.weekday()]} {d.day}. {MAANED[d.month - 1]}'


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
    <description>Varsler om avfallshenting i Horten kommune. Minner deg på hvilke avfallstyper som hentes neste dag.</description>
    <language>no</language>
    <lastBuildDate>{now_str}</lastBuildDate>
    <atom:link href="https://edrenate.github.io/horten-renovasjon-widget/avfall-feed.xml" rel="self" type="application/rss+xml"/>
    <managingEditor>post@horten.kommune.no (Horten kommune)</managingEditor>
    <ttl>60</ttl>{items_xml}
  </channel>
</rss>"""


def main():
    now = datetime.now(tz=OSLO)
    items_xml = ''

    for date_str in sorted(COLLECTIONS.keys()):
        pub_dt = pub_datetime(date_str)

        # Only include items whose pubDate has been reached
        if pub_dt > now:
            continue

        typer = COLLECTIONS[date_str]
        d = datetime.strptime(date_str, '%Y-%m-%d')
        uke = d.isocalendar()[1]
        ikoner = ' '.join(IKONER.get(t, '♻️') for t in typer)
        ts = typer_streng(typer)

        title = f'{ikoner} Husk avfallshenting i morgen \u2013 {ts}'
        desc = (
            f'Husk \u00e5 sette frem dunken(e) i morgen, {norsk_dato(d)} '
            f'(uke {uke}). F\u00f8lgende avfall hentes: {ts}. '
            f'Sjekk hentedager for din adresse p\u00e5 horten.kommune.no.'
        )

        items_xml += f"""
    <item>
      <title>{title}</title>
      <description>{desc}</description>
      <pubDate>{format_datetime(pub_dt)}</pubDate>
      <guid isPermaLink="false">horten-avfall-{date_str}</guid>
      <link>{ARTICLE_URL}</link>
    </item>"""

    feed = build_feed(items_xml, format_datetime(now))

    with open('avfall-feed.rss', 'w', encoding='utf-8') as f:
        f.write(feed)

    print(f'Feed generert: {items_xml.count("<item>")} items (per {now.strftime("%Y-%m-%d %H:%M %Z")})')


if __name__ == '__main__':
    main()
