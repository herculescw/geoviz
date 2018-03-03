# -*- coding: utf-8 -*-

"""Main module."""
import numpy as np
import pandas as pd
import plotly.offeline as py

from enum import Enum


def init_notebook_mode(connected=True):
    py.init_notebook_mode(connected=connected)


class MapScope(Enum):
    """
    Set the scope of the map.
    """
    world = 'world'
    usa = 'usa'
    europe = 'europe'
    asia = 'asia'
    africa = 'africa'
    north_america = 'north america'
    south_america = 'south america'


class LocationMode(Enum):
    """
    Determined that the set of locations used to match entries in `locations` to regions on the map.
    """
    ISO3 = 'ISO-3'
    USA_states = 'USA-states'
    country_names = 'country names'


class ColorScale(Enum):
    """
    The color scale.
    """
    blues = [[0, "rgb(5, 10, 172)"], [0.35, "rgb(40, 60, 190)"], [0.5, "rgb(70, 100, 245)"],
             [0.6, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [1, "rgb(220, 220, 220)"]]
    heatmap_cs = scl = [0, "rgb(150,0,90)"], [0.125, "rgb(0, 0, 200)"], [0.25, "rgb(0, 25, 255)"], \
                       [0.375, "rgb(0, 152, 255)"], [0.5, "rgb(44, 255, 150)"], [0.625, "rgb(151, 255, 0)"], \
                       [0.75, "rgb(255, 234, 0)"], [0.875, "rgb(255, 111, 0)"], [1, "rgb(255, 0, 0)"]


class BasePlot:
    def __init__(self, df, lon_col_name, lat_col_name):
        self.df = df
        self.data_point = []
        self.lon_col_name = lon_col_name
        self.lat_col_name = lat_col_name
        self.type = None
        self.locationmode = None

    def set_base_data_point(self, val_col_name, type='scattergeo', color='red', size=10, opacity=0.8,
                            locationmode=LocationMode.ISO3.value):
        self.type = type
        self.locationmode = locationmode

        data_point = dict(
            lon=self.df[self.lon_col_name],
            lat=self.df[self.lat_col_name],
            type=self.type,
            locationmode=self.locationmode,
            hoverinfo=val_col_name,
            text=self.df['val_col_name'],
            mode='markers',
            marker=dict(
                size=size,
                opacity=opacity,
                color=color
            )
        )
        self.data_point = [data_point]

    def set_layout(self, title, scope=MapScope.north_america.value, landcolor="rgb(212, 212, 212)",
                   subunitcolor="rgb(255, 255, 255)", countrycolor="rgb(255, 255, 255)", showland=True,
                   showlakes=True, lakecolor="rgb(255, 255, 255)", showsubunits=True, showcountries=True,
                   resolution=50):
        self.layout = dict(
            geo=dict(
                scope=scope,
                showland=showland,
                landcolor=landcolor,
                subunitcolor=subunitcolor,
                countrycolor=countrycolor,
                showlakes=showlakes,
                lakecolor=lakecolor,
                showsubunits=showsubunits,
                showcountries=showcountries,
                resolution=resolution,
                projection=dict(
                    type='conic conformal',
                    rotation=dict(
                        lon=-100
                    )
                ),
                lonaxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    range=[-140.0, -55.0],
                    dtick=5
                ),
                lataxis=dict(
                    showgrid=True,
                    gridwidth=0.5,
                    range=[20.0, 60.0],
                    dtick=5
                )
            ),
            title=title,
        )

    def merge_two_dicts(self, x, y):
        z = x.copy()
        z.update(y)
        return z

    def save_to_file(self, filename):
        fig = dict(data=self.data_point, layout=self.layout)
        py.plot(fig, filename=filename, auto_open=False)


class CategoryPlot(BasePlot):
    """
    Same Category data will be presented in same color. It also provides edge plotting.
    """

    def __init__(self, df, lon_col_name, lat_col_name):
        self.df = df
        self.data_point = []
        self.connection_path = []
        self.lon_col_name = lon_col_name
        self.lat_col_name = lat_col_name
        self.type = None

    def set_data_point(self, val_col_name, text_col_name, type='scattergeo', size=10, opacity=0.8, coloarscale='Viridis'
                       , locationmode=LocationMode.ISO3.value):
        """
        :param val_col_name:
        :param text_col_name:
        :param size:
        :param opacity:
        :param coloarscale:
        """
        unique_val = self.df[val_col_name].unique()
        temp_df = pd.DataFrame({val_col_name: unique_val})
        temp_df['color'] = np.random.randn(temp_df.size)
        result = pd.merge(left=self.df, right=temp_df, on=val_col_name)
        result['text'] = result[val_col_name] + ':' + result[text_col_name]
        self.type = type
        self.locationmode = locationmode

        data_point = dict(
            lon=result[self.lon_col_name],
            lat=result[self.lat_col_name],
            type=self.type,
            locationmode=self.locationmode,
            hoverinfo='text',
            text=result['text'],
            mode='markers',
            marker=dict(
                size=size,
                opacity=opacity,
                color=result['color'],
                coloarscale=coloarscale
            )
        )
        self.data_point = [data_point]

    def set_connection_path(self, df_paths, start_lon, start_lat, end_lon, end_lat):
        """
        :param df_paths:
        """
        for i in range(len(df_paths)):
            self.connection_path.append(
                dict(
                    type=self.type,
                    locationmode=self.locationmode,
                    lon=[df_paths[start_lon][i], df_paths[end_lon][i]],
                    lat=[df_paths[start_lat][i], df_paths[end_lat][i]],
                    mode='lines',
                    line=dict(
                        width=1,
                        color='blue',
                    )
                )
            )

    def plot(self, show_connection=False, in_notebook=True):
        """
        :param show_connection:
        :param in_notebook:
        :return:
        """
        if show_connection & in_notebook:
            if len(self.connection_path) == 0:
                raise ValueError("No path data, please use set_connection_path method to set up.")
            fig = dict(data=self.connection_path + self.data_point, layout=self.layout)
            py.iplot(fig)
        elif in_notebook:
            fig = dict(self.data_point, layout=self.layout)
            py.iplot(fig)
        else:
            raise NotImplemented
