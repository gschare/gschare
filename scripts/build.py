# Python 3.11.4

# meta
#   note: NO TITLE. title is in content.
#   template header into body
#   template content into body after header

# generate blog post file

from os.path import join, isdir, isfile
from os import makedirs, walk
from shutil import copy
import json

BLOG_JSON = 'blog.json'
SRC = 'src/'
TEMPLATES = 'templates/'
ASSETS = 'assets/'
BLOG = 'blog/'
GARDEN = 'garden/'
STYLESHEET = join(ASSETS, 'style.css')
HEADER = join(TEMPLATES, 'header.html')
META = join(TEMPLATES, 'meta.html')

DOCS = 'docs/'

# Pages that just sit in the root directory.
LOOSE_LEAVES = [
        ('index.html', 'home'),
        ('cv.html', None),
        ('404.html', None),
        ('now.html', 'now'),
        ]

def build_page(content, tab=None):
    # tab: which thing in the nav bar to highlight, if any.

    with open(META, 'r') as f:
        meta = f.read()
        split = meta.find('\n</body>')
        before_body, after_body = meta[:split+1], meta[split:]

    with open(HEADER, 'r') as f:
        header = f.read()

    page = before_body + header + content + after_body

    # todo: replace this with a beautifulsoup query of the id
    if tab is not None:
        page += f'<script>document.getElementById("nav-{tab}").style.textDecoration = "underline";</script>'

    return page

def build_page_from_source(src, **kwargs):
    with open(src, 'r') as f:
        content = f.read()
        return build_page(content, **kwargs)

def write_page(content, dest):
    with open(dest, 'w') as f:
        f.write(content)

def check_for_sources():
    sources = {
            BLOG: isdir(join(SRC, BLOG)),
            GARDEN: isdir(join(SRC, GARDEN)),
            ASSETS: isdir(join(SRC, ASSETS)),
            STYLESHEET: isfile(join(SRC, STYLESHEET)),
            TEMPLATES: isdir(TEMPLATES),
            HEADER: isfile(HEADER),
            META: isfile(META),
            '.htaccess': isfile(join(SRC, '.htaccess'))
        }

    for leaf, _ in LOOSE_LEAVES:
        sources[leaf] = isfile(join(SRC, leaf))

    missing = list(filter(lambda x: not sources[x], sources.keys()))
    if len(missing) > 0:
        raise Exception('Missing source files/directories:\n\t' + '\n\t'.join(missing))

def write_nojekyll():
    with open('.nojekyll', 'w') as f:
        f.write('')

def copy_assets():
    makedirs(join(DOCS, ASSETS), exist_ok=True)
    with open(join(SRC, STYLESHEET), 'r') as s, open(join(DOCS, STYLESHEET), 'w') as d:
        d.write(s.read())
    copy(join(SRC, ASSETS, 'cv.pdf'), join(DOCS, ASSETS, 'cv.pdf'))

def write_blog():
    makedirs(join(DOCS, BLOG), exist_ok=True)

    with open(BLOG_JSON, 'r') as f:
        blog_data = json.load(f)

    index = '<title>Blog</title><main><div><h2>Posts</h2><ul class="nobullet">'

    for root, _, posts in walk(join(SRC, BLOG)):
        for post in posts:
            if post[0] == '.':
                continue
            page = build_page_from_source(join(root, post), tab="blog")
            write_page(page, join(DOCS, BLOG, post))

            title = blog_data[post]['title']
            preview = blog_data[post]['preview']

            index_item = ('<li><a href="' + post + '"><p><b>' +
                          title + '</b><br><i>' + preview + '</i></p></a></li>')

            index += index_item

    index += '</ul></div></main>'
    write_page(build_page(index, tab="blog"), join(DOCS, BLOG, 'index.html'))

def write_garden():
    makedirs(join(DOCS, GARDEN), exist_ok=True)

    for garden, _, files in walk(join(SRC, GARDEN)):
        for file in files:
            if file[0] == '.':
                continue
            page = build_page_from_source(join(garden, file), tab="garden")
            write_page(page, join(DOCS, GARDEN, file))

def main():
    check_for_sources()

    # write `docs/`
    makedirs(DOCS, exist_ok=True)

    # write `docs/.nojekyll`
    write_nojekyll()

    # write `docs/.htaccess`
    with open(join(SRC, '.htaccess'), 'r') as src, open(join(DOCS, '.htaccess'), 'w') as dst:
        dst.write(src.read())

    # write `docs/assets/`
    copy_assets()

    # write misc pages
    for p, tab in LOOSE_LEAVES:
        write_page(build_page_from_source(join(SRC, p), tab=tab), join(DOCS, p))

    # write `docs/blog/`
    write_blog()

    # write `docs/garden/`
    write_garden()

if __name__ == '__main__':
    main()
