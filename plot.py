from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D
import pandas as pd
from pandas import DataFrame
import numpy as np

from livesplit_data import LiveSplitData
from theme import Theme
from graph import Graph


class Plot():
    def __init__(self, livesplit_data: LiveSplitData, split_name, split_index, theme: Theme, show_outliers=False):
        # retarded I know
        self.fig, ax = plt.subplots()
        self.ax: Axes = ax

        self.lsd = livesplit_data
        self.split_name = split_name
        self.split_index = split_index
        self.theme = theme
        self.show_outliers = show_outliers
        
        self.fig.patch.set_facecolor(self.theme.figure_color)
        self.ax.set_facecolor(self.theme.axes_color)
        self.ax.tick_params(colors=self.theme.ticks_color)
        self.ax.xaxis.label.set_color(self.theme.xy_label_color)
        self.ax.yaxis.label.set_color(self.theme.xy_label_color)

        # annotation init
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(-50,17),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.get_bbox_patch().set_facecolor("white")
        self.annot.get_bbox_patch().set_alpha(0.8)
        self.annot.set_zorder(100)

        self.annot.set_visible(False)
        

    def hist(self, seg_times) -> Figure:
        ''' 
        Plot a histogram given `seg_times`.

        `seg_times` is a list of datetime objects which is used to calculate the interval used to plot dates on the X axis.
        '''

        #draw graph
        self.ax.hist(seg_times, color=self.theme.hist_color)

        # x axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter('%M:%S')(x)
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(xfmt))

        #set headers
        self.set_axes_headers(title=f"{self.split_name} Histogram", title_color=self.theme.title_color)

        #labels
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Frequency")
        self.ax.set_axisbelow(False)

        return self.fig
    
    def moving_avg(self, segment_times: DataFrame, avg_segment_times: DataFrame) -> Figure:
        #draw graph
        colors = np.where(segment_times["is_from_pb"], self.theme.pb_color, self.theme.scatter_color)
        alphas = np.where(segment_times["is_from_pb"], 1, 0.3)
        self.ax.scatter(segment_times.index.values+1, segment_times["seg_times"], s=10, c=colors, alpha=alphas)
        self.ax.plot(avg_segment_times["avg_indexes"], avg_segment_times["avg_times"], linewidth=1.5, c=self.theme.plot_color)

        # y axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter('%M:%S')(x)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(xfmt))

        #set headers
        self.set_axes_headers(title=f"{self.split_name} Time Over Attempts", title_color=self.theme.title_color)

        #labels
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Split Time")
        self.ax.set_axisbelow(True)

        self.seg_times = segment_times["seg_times"]

        return self.fig

    def attempts_over_time(self) -> Figure:
        AOT_dates = self.lsd.AOT_dates
        AOT_attempts = self.lsd.AOT_attempts

        # testing: show most played date and time
        """ most_time = relativedelta(hours=0)
        for i, time_played in enumerate(self.lsd.daily_time_played):
            time_played: relativedelta

            if self.rd_in_seconds(time_played) > self.rd_in_seconds(most_time):
                most_time = time_played
                print(i)
                print(AOT_dates[i])

        print(most_time)
        print(self.rd_in_seconds(most_time)) """

        self.ax.plot(AOT_dates, AOT_attempts, c=self.theme.plot_color, label="All")
        self.ax.plot(self.lsd.unique_finished_dates, self.lsd.finished_attempts, c=self.theme.plot2_color, linewidth=1.5, label="Finished")

        # x axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%b %d '%y")(x)
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(6))

        self.set_axes_headers(title="Attempts Over Time", title_color=self.theme.title_color)

        self.ax.legend(loc="upper left").set_draggable(True)

        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Attempts")
        self.ax.set_axisbelow(True)

        return self.fig

    def imp_over_attempts(self) -> Figure:
        completed_times = self.lsd.finished_times
        abs_indexes = self.lsd.finished_indexes

        self.ax.plot(abs_indexes, completed_times, c=self.theme.plot_color, linewidth=1.5)

        # y axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%H:%M:%S")(x)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator('auto'))

        self.set_axes_headers(title="Improvement Over Attempts", title_color=self.theme.title_color)
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig

    def imp_over_time(self) -> Figure:
        finished_times = self.lsd.finished_times

        self.ax.scatter(self.lsd.finished_dates, finished_times, c=self.theme.scatter_color, s=10, alpha=0.3)

        # y axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%H:%M:%S")(x)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator('auto'))

        # x axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%b %d '%y")(x)
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(6))

        self.set_axes_headers(title="Improvement Over Time", title_color=self.theme.title_color)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig

    def personal_best_over_time(self) -> Figure:
        """
        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
        """
        pb_dates = self.lsd.pb_dates
        pb_times = self.lsd.pb_times

        self.ax.plot(
            pb_dates, 
            pb_times, 
            color=self.theme.plot_color, 
            linewidth=1.5, 
            marker="o", 
            markersize=3.5, 
            markerfacecolor=self.theme.scatter_color, 
            markeredgecolor=self.theme.scatter_color
        )

        # y axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%H:%M:%S")(x)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator('auto'))

        # x axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%b %d '%y")(x)
        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(6))

        self.set_axes_headers(title="Personal Best Over Time", title_color=self.theme.title_color)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig
    
    def personal_best_over_attempts(self) -> Figure:
        pb_times = self.lsd.pb_times
        pb_abs_indexes = self.lsd.pb_abs_indexes

        self.ax.plot(
            pb_abs_indexes, 
            pb_times, 
            color=self.theme.plot_color, 
            linewidth=1.5, 
            marker="o", 
            markersize=3.5, 
            markerfacecolor=self.theme.scatter_color, 
            markeredgecolor=self.theme.scatter_color
        )

        # y axis formatting
        xfmt = lambda x, pos: mdates.DateFormatter("%H:%M:%S")(x)
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(xfmt))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator('auto'))

        self.set_axes_headers(title="Personal Best Over Attempts", title_color=self.theme.title_color)
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig

    def hover_plot(self, event: MouseEvent, graph: Graph):
        """
        Check when hovering over a plot line, proceed to update the annotation.

        Depending on the `type_graph` different update functions are called. This is because 
        different graphs require different annotations with different data types.
        """
        plot_data: list[Line2D] = self.ax.get_lines()
        if event.inaxes != self.ax or len(plot_data) < 1:
            return

        # assume 1 line
        line = plot_data[0]
        if len(plot_data) == 2:
            # check which line is being hovered over
            if plot_data[1].contains(event)[0]:
                line = plot_data[1]

        hovering_over_line, pointlist = line.contains(event)

        if hovering_over_line:
            match graph:
                case Graph.ATTEMPTS_OVER_TIME:
                    self.update_attempts_over_time_annot(pointlist, line)
                case Graph.PB_OVER_TIME:
                    self.update_pb_over_time_annot(pointlist, line)
                case Graph.PB_OVER_ATTEMPTS:
                    return
            self.annot.set_visible(True)
            self.fig.canvas.draw_idle()
        else:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()

    def update_pb_over_time_annot(self, pointlist: dict, line: Line2D):
        """
        Format the data for the PB Over Time graph and update the annotation.
        """
        index = pointlist["ind"][0]
        day: datetime = line.get_xdata()[index]
        day = day.strftime("%b %d %Y")
        pb_time: datetime = line.get_ydata()[index]
        
        improved_by = "_"
        if index != 0:  
            previous_pb_time: datetime = line.get_ydata()[index-1]
            difference = previous_pb_time - pb_time
            improved_by = self.format_timedelta(difference)

        pb_time = pb_time.strftime("%H:%M:%S.%f")[:10]

        # set coordinates for annotation object relative to object being annotated
        pos = line.get_xydata()[index]
        self.annot.xy = pos

        self.annot.set_text(f"#{index+1}\n{day}\n\nPB: {pb_time}\nImproved by {improved_by}")

    def update_attempts_over_time_annot(self, pointlist: dict, line: Line2D):
        """
        Format the data for the Attempts Over Time graph and update the annotation.
        """
        index = pointlist["ind"][0]
        day: datetime = line.get_xdata()[index]
        day = day.strftime("%b %d %Y")
        total_attempts = line.get_ydata()[index]
        daily_time_played: relativedelta = self.lsd.daily_time_played[index]
        daily_time_played = self.format_relativedelta(daily_time_played)

        # check for first index
        total_attempts_previous_session = line.get_ydata()[index-1]
        if index == 0:
            total_attempts_previous_session = 0
        daily_attempts = total_attempts - total_attempts_previous_session

        # set coordinates for annotation object relative to object being annotated
        self.annot.xy = line.get_xydata()[index]

        self.annot.set_text(f"Total: {total_attempts}\nDaily: {daily_attempts}\nTime Played: {daily_time_played}\nDate: {day}")

    def hover_scatter(self, event: MouseEvent):
        """
        Check when hovering over a scatter node, proceed to update the annotation.
        """
        if event.inaxes != self.ax:
            return
        
        scatter_data = self.ax.collections[0]
        hovering_over_scatter_point, points_on_x_axis = scatter_data.contains(event)

        if hovering_over_scatter_point:
            self.update_scatter_annot(points_on_x_axis, scatter_data)
            self.annot.set_visible(True)
            self.fig.canvas.draw_idle()
        else:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()

    def update_scatter_annot(self, points_on_x_axis: dict, scatter_data: PathCollection):
        pos = scatter_data.get_offsets()[points_on_x_axis["ind"][0]]
        self.annot.xy = pos

        attempt_num = points_on_x_axis["ind"][0] + 1
        formatted_time = self.seg_times[attempt_num-1].strftime("%M:%S.%f")[:9]
        self.annot.set_text(f"#{attempt_num}\n{formatted_time}")

    def set_axes_headers(self, title, title_color):
        game_name = self.lsd.game_name
        category = self.lsd.game_category
        variables = self.lsd.variables
        variable_string = ""

        available_variables = self.lsd.available_variables
        ordered_variables = []

        #variables must be present in lss file
        if available_variables != 0 and len(variables) != 0 :
            for available_var in available_variables:
                for var in variables:
                    if available_var == var.attrib.get('name'):
                        ordered_variables.append(var)

            for variable in ordered_variables:
                if variable.text.lower() in ('yes', 'no'):
                    variable_string += f"{variable.attrib.get('name')}={variable.text}, "
                    continue
                variable_string += f"{variable.text}, "
        
            variable_string = variable_string.removesuffix(', ')
            variable_string = f"({variable_string})"

        self.ax.set_title(f"{game_name} - {category} {variable_string}\n{title}", color=title_color, loc='center', wrap=True)

    def format_timedelta(self, td: timedelta) -> str:
        """
        Helper function that converts a `timedelta` object to a user friendly string.

        Examples: `2h 24m 10s` or `17m 56s` or `28s`

        Takes a parameter of type `timedelta`.
        """
        seconds = td.seconds
        hours = seconds // 3600
        minutes = (seconds - (hours*3600)) // 60
        remaining_seconds = seconds - (hours*3600) - (minutes*60)

        formatted_str = ""
        if hours != 0:
            formatted_str += f"{hours}h "
        if minutes != 0:
            formatted_str += f"{minutes}m "

        if hours == 0 and minutes == 0:
            formatted_str += f"{remaining_seconds}.{str(td.microseconds)[:1]}s "
        elif remaining_seconds != 0:
            formatted_str += f"{remaining_seconds}s "

        return formatted_str
    
    def format_relativedelta(self, rd: relativedelta) -> str:
        """
        Helper function that converts a `relativedelta` object to a user friendly string.
        """
        
        hours = rd.hours
        hours += rd.days * 24

        formatted_str = ""
        if hours != 0:
            formatted_str += f"{hours}h "

        if rd.minutes != 0:
            formatted_str += f"{rd.minutes}m "

        if rd.seconds != 0:
            formatted_str += f"{rd.seconds}s "

        return formatted_str
    
    def rd_in_seconds(self, rd: relativedelta) -> int:
        return rd.days*86400 + rd.hours*3600 + rd.minutes*60 + rd.seconds