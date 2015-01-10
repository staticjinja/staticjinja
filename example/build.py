import staticjinja

# You can define your own Jinja2 filters and inject them.
myFilters = { 'filter1': lambda x:"hello world!", 'filter2': lambda x:x.lower() }

if __name__ == "__main__":
    site = staticjinja.make_site(filters=myFilters)
    #site = staticjinja.make_site()
    site.render()
