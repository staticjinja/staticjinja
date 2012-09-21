staticjinja
===========

Script to easily deploy static sites using the extremely handy [jinja2](http://jinja.pocoo.org/docs/) templating language.

Requirements
------------

* jinja2 (`pip install jinja2`)
* (optional, for automatic compilation) watchdog (`pip install watchdog`)

Setup
-----

To compile the templates run `python build.py`. This will look execute the `main` function in `build.py` (which is set by default to build the `index.html` file inside of `./templates`).

To compile additional pages, you will need to add more functions specifying how to compile each page. For pages which are loading any data, and therefore don't require a context, adding the line `build_template(env, 'mypage.html')` to `main` is sufficient. For pages which require a context of some sort, you will need to write a custom function that `main` calls, passing context data as extra arguments to `build_template`.

Automatic Compilation
---------------------

If you installed `watchdog`, you can run 'python build.py --watch' to automatically recompile templates whenever a change is made.
