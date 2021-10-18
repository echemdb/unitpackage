class Plot:
    def __init__(self, entry):
        self._entry = entry

    @property
    def figure(self):
        import plotly.graph_objects

        fig = plotly.graph_objects.Figure()

        df = self._entry.df

        fig.add_trace(plotly.graph_objects.Scatter(x=df['U'], y=df['j'], mode='lines'))

        fig.update_layout(template="simple_white", showlegend=True, autosize=True, width=450, height=350, margin=dict(l=70, r=70, b=70, t=70, pad=7))
        return fig

    @property
    def html(self):
        import plotly.io
        return '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + \
            plotly.io.to_html(self.figure, include_plotlyjs=False, full_html=False)

    def _ipython_display_(self):
        return self.figure._ipython_display_()
