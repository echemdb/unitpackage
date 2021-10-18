def define_env(env):
    @env.macro
    def table_from_csv(csvfile):
        from echemdb.markdown_pieces import get_table
        return get_table(csvfile)

    @env.macro
    def periodic_table():
        from echemdb.website.legacy.markdown_pieces import get_periodic_table_span
        return get_periodic_table_span()

    @env.macro
    def make_element_page(elementname):
        from echemdb.website.legacy.make_pages import get_element_page_contents
        return get_element_page_contents(elementname)

    @env.macro
    def make_systems_page():
        from echemdb.website.legacy.make_pages import get_systems_page_contents
        return get_systems_page_contents()

    @env.macro
    def make_element_surface_page(elementname, surfacename):
        from echemdb.website.legacy.make_pages import get_element_surface_page_contents
        return get_element_surface_page_contents(elementname, surfacename)

    @env.macro
    def plotly(names, paths):
        from echemdb.data.legacy.build_data import get_plotly_plot
        return get_plotly_plot(names, paths)
