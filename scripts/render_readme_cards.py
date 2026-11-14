#!/usr/bin/env python3
"""Refresh public GitHub activity and render self-contained animated README SVGs.

Python standard library only. STATIC=1 disables animations. --refresh updates
data/contributions.json; a failed refresh exits before replacing existing data.
"""
import argparse
import base64
import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'Abhay122710'
STATIC = os.getenv('STATIC') == '1'
OUT = Path(os.getenv('OUTPUT_DIR', str(ROOT / 'cards')))
INK, MUTED, BLUE = '#e6edf3', '#9aa8ba', '#5b9dff'


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.labels = {}, {}
        self.tooltip, self.label = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and a.get('data-date'):
            self.cells[a['id']] = a['data-date']
        if tag == 'tool-tip' and a.get('for'):
            self.tooltip, self.label = a['for'], []

    def handle_data(self, value):
        if self.tooltip:
            self.label.append(value)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tooltip:
            self.labels[self.tooltip] = ''.join(self.label).strip()
            self.tooltip = None


def refresh():
    url = f'https://github.com/users/{USER}/contributions'
    req = urllib.request.Request(url, headers={'User-Agent': 'Abhay-profile-cards', 'Accept-Language': 'en-US'})
    with urllib.request.urlopen(req, timeout=45) as response:
        html = response.read().decode('utf-8')
    parser = CalendarParser()
    parser.feed(html)
    today = datetime.now(timezone.utc).date()
    days = []
    for cell, day in parser.cells.items():
        if date.fromisoformat(day) > today:
            continue
        label = parser.labels.get(cell, '')
        match = re.match(r'(No|[\d,]+) contributions?\b', label)
        if not match:
            raise ValueError(f'Cannot read contribution count for {day}; retaining last snapshot')
        count = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
        days.append({'date': day, 'count': count})
    days.sort(key=lambda d: d['date'])
    if len(days) < 350 or len({d['date'] for d in days}) != len(days):
        raise ValueError('Incomplete contribution calendar; retaining last snapshot')
    for left, right in zip(days, days[1:]):
        if date.fromisoformat(right['date']) - date.fromisoformat(left['date']) != timedelta(days=1):
            raise ValueError('Contribution calendar has gaps')
    if days[-1]['date'] != today.isoformat():
        raise ValueError('Contribution calendar is not current')
    payload = {'username': USER, 'source': url, 'as_of': today.isoformat(), 'days': days}
    destination = ROOT / 'data/contributions.json'
    destination.parent.mkdir(exist_ok=True)
    temp = destination.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, indent=2) + '\n')
    temp.replace(destination)


def text(x, y, value, size=16, fill=INK, weight=400, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'


def rect(x, y, w, h, fill, radius=0, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" {extra}/>'


def arrow(x, y, color):
    return f'<g transform="translate({x},{y})"><path class="arrow" d="M0 18L18 0M0 0H18V18" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>'


def group(body, delay=0):
    return f'<g class="enter" style="animation-delay:{delay}s">{body}</g>'


def svg(name, title, description, body, height, width=960):
    fonts = ''.join(f"@font-face{{font-family:Kanit;src:url(data:font/woff;base64,{base64.b64encode((ROOT / 'fonts' / f'kanit-{w}.woff').read_bytes()).decode()}) format('woff');font-weight:{w};}}" for w in [400, 700])
    animation = '' if STATIC else '''
      @keyframes enter{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
      @keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}
      @keyframes grow{from{transform:scaleY(.02)}to{transform:scaleY(1)}}
      @keyframes drift{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}
      .enter{animation:enter .8s both}.pulse{animation:pulse 3s ease-in-out infinite}
      .bar{transform-box:fill-box;transform-origin:center bottom;animation:grow 1.1s both}
      .arrow{animation:drift 3s ease-in-out infinite}
      @media(prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;transform:none!important}}
    '''
    source = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
    <title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
    <defs><linearGradient id="shade" x2="1" y2="1"><stop stop-color="#171c25"/><stop offset="1" stop-color="#0c0c0c"/></linearGradient></defs>
    <style>{fonts}text{{font-family:Kanit,Arial,sans-serif}}{animation}</style>
    {rect(1,1,width-2,height-2,'url(#shade)',20,extra='stroke="#293241"')}{body}</svg>'''
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f'{name}.svg').write_text(source)


def render():
    payload = json.loads((ROOT / 'data/contributions.json').read_text())
    days = payload['days']
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    longest, run = 0, 0
    for day in days:
        run = run + 1 if day['count'] else 0
        longest = max(longest, run)
    current = 0
    eligible = days[:-1] if days[-1]['count'] == 0 else days
    for day in reversed(eligible):
        if not day['count']:
            break
        current += 1
    best = max(days, key=lambda d: d['count'])
    photo = base64.b64encode((ROOT / 'assets/portrait-small.png').read_bytes()).decode()
    hero = text(40,48,'ABHAY / DEVELOPER & CREATOR',14,BLUE,700,extra='letter-spacing="2"')
    hero += group(text(38,132,'Abhay',78,weight=700)+text(38,211,'Chaudhary.',78,weight=700),.1)
    hero += group(text(42,254,'Software. Games. Intelligent experiences.',22),.3)
    hero += group(text(42,287,'CSE · Graphics & Gaming · UPES, Dehradun',17,MUTED),.5)
    hero += f'<circle cx="49" cy="326" r="4" fill="{BLUE}" class="pulse"/>' + text(62,332,'BUILDING WITH CURIOSITY',12,MUTED,700,extra='letter-spacing="2"')
    hero += '<circle cx="783" cy="185" r="132" fill="#142746" stroke="#294b78"/>'
    hero += group(f'<image x="632" y="28" width="303" height="324" href="data:image/png;base64,{photo}"/>',.3)
    svg('hero','Abhay Chaudhary — software, games and intelligent experiences','Computer Science and Engineering student at UPES, specializing in Graphics and Gaming.',hero,370)

    heat = text(36,44,'A YEAR IN CODE',14,BLUE,700,extra='letter-spacing="2"') + text(924,44,f'{total:,} contributions',19,weight=700,extra='text-anchor="end"')
    start = date.fromisoformat(days[0]['date'])
    start -= timedelta(days=(start.weekday()+1)%7)
    colors = ['#202b3c','#1a3b68','#245da4','#3b82d9','#75b6ff']
    max_count = max(d['count'] for d in days) or 1
    last_month = None
    for index, day in enumerate(days):
        dt = date.fromisoformat(day['date'])
        col, row = divmod((dt-start).days,7)
        x,y = 53+col*16,90+row*16
        if dt.month != last_month and (dt.day == 1 or index == 0):
            heat += text(x,77,calendar.month_abbr[dt.month],11,MUTED)
            last_month = dt.month
        level = 0 if day['count']==0 else min(4,1+int(3*(day['count']/max_count)**.5))
        heat += group(f'<rect x="{x}" y="{y}" width="12" height="12" rx="3" fill="{colors[level]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>', .5+col*.013)
    heat += text(36,224,'Public GitHub contribution calendar · refreshed daily',12,MUTED)
    heat += text(924,224,payload['as_of'],12,MUTED,extra='text-anchor="end"')
    svg('heatmap','GitHub contribution calendar',f'{total} contributions across {active} active days. Data through {payload["as_of"]}.',heat,246)

    monthly = defaultdict(int)
    for day in days:
        monthly[day['date'][:7]] += day['count']
    months = list(monthly.items())
    chart = text(36,44,'SMALL STEPS. VISIBLE PROGRESS.',14,BLUE,700,extra='letter-spacing="2"')
    stats = [('CURRENT STREAK',f'{current} day' + ('' if current == 1 else 's')),('LONGEST STREAK',f'{longest} day' + ('' if longest == 1 else 's')),('ACTIVE DAYS',str(active)),('BUSIEST DAY',str(best['count']))]
    for i,(label,value) in enumerate(stats):
        x=36+i*234
        chart += text(x,83,label,11,MUTED,700,extra='letter-spacing="1"')+text(x,123,value,31,weight=700)
    chart += text(738,143,best['date'],11,MUTED)
    maximum = max(monthly.values()) or 1
    step = 888 / len(months)
    for i,(month,count) in enumerate(months):
        x=36+i*step
        h=95*count/maximum
        fill=BLUE if count==maximum else '#334d70'
        chart += rect(round(x,1),260-h,round(step-20,1),h,fill,5,extra=f'class="bar" style="animation-delay:{.8+i*.06}s"')
        chart += text(round(x+(step-20)/2,1),250-h,count,11,MUTED,extra='text-anchor="middle"')
        chart += text(round(x+(step-20)/2,1),281,datetime.strptime(month,'%Y-%m').strftime('%b'),12,MUTED,extra='text-anchor="middle"')
    chart += text(36,312,'Monthly totals within the calendar window · first and current months may be partial',12,MUTED)
    svg('activity','Monthly GitHub activity',f'Current streak {current} days; longest streak {longest} days in this calendar window. A current streak may end yesterday.',chart,332)

    tiles=[('build','01','BUILD','#5b9dff','Full-stack applications','React · TypeScript · Supabase'),('think','02','THINK','#b79bff','AI with useful memory','Python · RAG · Knowledge graphs'),('play','03','PLAY','#f5bc61','Interactive worlds','Unity · C# · Blender')]
    for i,(name,num,label,color,line,stack) in enumerate(tiles):
        body=rect(1,1,310,4,color,2)+text(24,43,num,14,color,700)
        body+=group(text(24,102,label,43,weight=700)+text(24,139,line,17)+text(24,171,stack,12,MUTED),1+i*.12)
        body+=arrow(273,26,color)
        svg(name,label,line+'. '+stack,body,202,312)

    projects=[('vendorplus','01 / COMMERCE','Vendor+','A smarter storefront for local shops.','Product management, demand forecasting and order alerts.','React · TypeScript · Supabase · Python',BLUE),('mnemosyne','02 / ARTIFICIAL INTELLIGENCE','Mnemosyne','Give a codebase a long-term memory.','Local knowledge graphs turn past bugs into useful context.','Python · Cognee · Ollama · RAG','#b79bff'),('geometry','03 / GAME DEVELOPMENT','Geometry Dash-style 2D game','Built to move. Designed to challenge.','Multiple player modes, gravity switching and collision handling.','Unity · C# · Raycasting · Physics','#f5bc61')]
    for i,(name,tag,title,line,desc,stack,color) in enumerate(projects):
        body=text(32,38,tag,12,color,700,extra='letter-spacing="1.5"')
        body+=group(text(32,85,title,31,weight=700)+text(32,119,line,19)+text(32,148,desc,15,MUTED),1.3+i*.12)
        body+=text(32,183,stack,13,color)+arrow(898,37,color)
        svg('project-'+name,title,line+' '+desc+' '+stack,body,208)

    footer=text(36,49,'LET’S BUILD SOMETHING USEFUL.',25,weight=700)+text(36,80,'Software development · AI applications · Games & visual design',16,MUTED)+arrow(892,42,BLUE)
    svg('connect','Connect with Abhay on LinkedIn','Open to collaborating on software, AI, and game development projects.',footer,111)
    print(f'Rendered 10 cards in {OUT}; {total} contributions, {active} active days, longest streak {longest}.')


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--refresh', action='store_true')
    if args.parse_args().refresh:
        refresh()
    render()
