import click
import frontmatter
import parsedatetime
import re
import os
import sys
import yaml

from datetime import datetime
from github import Github
from pytz import timezone

from dotenv import load_dotenv
load_dotenv()

APP_NAME = 'sup'

DEFAULT_CONFIG = {
    'frontmatter': {
        'layout': 'post',
    },

    'github': {
        'dir': '_posts',
    },
}

CONFIG = {}

cal = parsedatetime.Calendar()

def create_post(entry):
    pattern = re.compile(r'((?P<date>[^:]*):\s+)?\s*(?P<body>.*)', re.MULTILINE | re.DOTALL)
    match = pattern.search(entry)

    metadata = {}
    metadata.update(CONFIG.get('frontmatter', {}))
    metadata.update(match.groupdict())

    if metadata['date']:
        metadata['date'], _ = cal.parseDT(datetimeString=metadata['date'], tzinfo=timezone('UTC'))
    else:
        metadata['date'] = datetime.now(tz=timezone('UTC'))

    categories = re.findall(r'@([^@\s]+)\b', metadata['body'])
    if categories:
        metadata['categories'] = categories
    tags = re.findall(r'#([^#\s]+)\b', metadata['body'])
    if tags:
        metadata['tags'] = tags

    content = metadata['body'].strip()
    del metadata['body']

    return frontmatter.Post(content, **metadata)

@click.command()
@click.argument('entry', nargs=-1)
def cli(entry):
    if not entry:
        click.echo('sup', err=True)
        sys.exit(1)

    post = create_post(' '.join(entry))

    dir = CONFIG['github'].get('dir', '_posts')
    filename = post['date'].strftime('%Y-%m-%d-%H%M%S')
    post['date'] = post['date'].strftime('%Y-%m-%d %H:%M:%S')
    path = f'{dir}/{filename}.md'
    message = 'sup'
    content = frontmatter.dumps(post)

    params = {}

    if CONFIG['github'].get('branch'):
        params['branch'] = CONFIG['github']['branch']

    github = Github(CONFIG['github']['token'])
    repo = github.get_user().get_repo(CONFIG['github']['repo'])

    response = repo.create_file(
        path,
        message,
        content,
        **params
    )

    click.echo(response['content'].html_url)

def main():
    global CONFIG

    CONFIG.update(DEFAULT_CONFIG)

    with open(os.path.join(click.get_app_dir(APP_NAME), 'config.yml')) as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
        CONFIG.update(config)

    cli(auto_envvar_prefix='SUP')

if __name__ == '__main__':
    main()
