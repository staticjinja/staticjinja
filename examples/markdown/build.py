# build.py
#!/usr/bin/env python3
import os

# Markdown to HTML library
# https://pypi.org/project/Markdown/
import markdown

from staticjinja import Site

markdowner = markdown.Markdown(output_format="html5")


def md_context(template):
    with open(template.filename) as f:
        markdown_content = f.read()
        return {"post_content_html": markdowner.convert(markdown_content)}


def render_md(site, template, **kwargs):
    # Given a template such as posts/post1.md
    # Determine the post's title (post1) and it's directory (posts/)
    directory, fname = os.path.split(template.name)
    post_title, _ = fname.split(".")

    # Determine where the result will be streamed (build/posts/post1.html)
    out_dir = os.path.join(site.outpath, directory)
    post_fname = "{}.html".format(post_title)
    out = os.path.join(out_dir, post_fname)

    # Render and stream the result
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    post_template = site.get_template("_post.html")
    post_template.stream(**kwargs).dump(out, encoding="utf-8")


site = Site.make_site(
    searchpath="src",
    outpath="build",
    contexts=[(".*.md", md_context)],
    rules=[(".*.md", render_md)],
)

site.render()
