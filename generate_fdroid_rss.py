import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta

response = requests.get('https://f-droid.org/repo/index-v2.json')
data = response.json()

fg = FeedGenerator()
fg.title('F-Droid Updated Apps')
fg.link(href='https://f-droid.org', rel='alternate')
fg.description('New Updated from F-Droid')

now = datetime.now(timezone.utc)

added_since = now - timedelta(days=10)

for package_name, package in data['packages'].items():
    versions_with_updated = [v for v in package.values() if 'lastUpdated' in v]
    
    if not versions_with_updated:
        continue
    
    latest_version = max(versions_with_updated, key=lambda v: v['lastUpdated'])
    
    updated_date = datetime.fromtimestamp(latest_version['lastUpdated'] / 1000, tz=timezone.utc)
    if updated_date >= added_since:
        fe = fg.add_entry()

        if isinstance(latest_version.get('name'), dict):
            fe.title(package_name)
        else:
            fe.title(latest_version.get('name', 'Unnamed Application'))

        fe.link(href='https://f-droid.org/packages/' + package_name)

        summary = latest_version.get('summary')
        if isinstance(summary, dict):
            summary = summary.get('en-US', 'No summary available')
        else:
            summary = str(summary if summary else 'No summary available')

        fe.description(summary)

with open('rss.xml', 'w') as f:
    f.write(fg.rss_str(pretty=True).decode('utf-8'))
