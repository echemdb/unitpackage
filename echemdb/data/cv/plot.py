# ********************************************************************
#  This file is part of echemdb.
#
#        Copyright (C) 2021 Albert Engstfeld
#        Copyright (C) 2021 Johannes Hermann
#        Copyright (C) 2021 Julian Rüth
#        Copyright (C) 2021 Nicolas Hörmann
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

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

    @property
    def figure_original(self):
        import plotly.graph_objects

        fig = plotly.graph_objects.Figure()

        df = self._entry.df_original

        fig.add_trace(plotly.graph_objects.Scatter(x=df['U'], y=df['j'], mode='lines'))

        fig.update_layout(template="simple_white", showlegend=True, autosize=True, width=450, height=350, margin=dict(l=70, r=70, b=70, t=70, pad=7))
        return fig

    @property
    def html_original(self):
        import plotly.io
        return '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>' + \
            plotly.io.to_html(self.figure_original, include_plotlyjs=False, full_html=False)

    def _ipython_display_(self):
        return self.figure._ipython_display_()
