import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

response = requests.get('https://f-droid.org/repo/index-v2.json')
data = response.json()

fg = FeedGenerator()
fg.title('F-Droid New Apps')
fg.link(href='https://f-droid.org', rel='alternate')
fg.description('New apps from F-Droid')

now = datetime.now(timezone.utc)

for package in data['packages']:
    updates = [p for p in data['packages'][package] if p.get('suggestedVersionCode') and p['obsoletes'] == 9223372036854775807]
    if not updates:
        continue
    newest_update = sorted(updates, key=lambda x: x['added'], reverse=True)[0]

    added_date = datetime.fromisoformat(newest_update['added'][:-1]) 
    if (now - added_date).days <= 2:  
        app = [a for a in data['apps'] if a['packageName'] == package][0]

        fe = fg.add_entry()
        fe.title(app['name'])
        fe.link(href='https://f-droid.org/packages/' + package)
        fe.description(app['summary'])

        icon_url = 'https://f-droid.org/repo/' + app['icon']
        icon_response = requests.get(icon_url)
        if icon_response.status_code == 200:
            fe.logo(icon_url)

with open('rss.xml', 'w') as f:
    f.write(fg.rss_str(pretty=True).decode('utf-8'))
