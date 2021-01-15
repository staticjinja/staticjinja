Example: markdown
=================

This example shows how you can use staticjinja for a personal blog. Each
blog post is written in markdown, and the markdown is rendered to html with the
``markdown`` library. Then, this html content is inserted into a ``_post.html``
template.

This shows off two of staticjinja's features:

1. Custom context generators: transform the markdown content to html
   content.
2. Custom render rules: properly map the input file location ``posts/post1.md``
   to the output location ``posts/post1.html``.

For more info see the `documentation walkthrough`_.

.. _`documentation walkthrough`: https://staticjinja.readthedocs.io/en/stable/user/advanced.html#rendering-rules
