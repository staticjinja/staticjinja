"""Minimal python build script from
https://staticjinja.github.io/staticjinja/user/advanced.html#using-custom-build-scripts
"""

from staticjinja import Site

if __name__ == "__main__":
    site = Site.make_site()
    # diable automatic reloading
    site.render(use_reloader=False)
