from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D

from livesplit_data import LiveSplitData
from theme import Theme


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
        

    def hist(self, seg_times):
        ''' 
        Plot a histogram given `seg_times`.

        `seg_times` is a list of datetime objects which is used to calculate the interval used to plot dates on the X axis.
        '''

        #draw graph
        self.ax.hist(seg_times, color=self.theme.hist_color)

        #set ticks
        interval_times = self.lsd.get_dynamic_interval(seg_times, ticks=9, format='%M:%S')
        self.ax.set_xticks(interval_times)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

        #set headers
        self.set_axes_headers(title=f"{self.split_name} Histogram", title_color=self.theme.title_color)

        #labels
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Frequency")
        self.ax.set_axisbelow(False)

        return self.fig
    
    def moving_avg(self, seg_times, seg_indexes, avg_times, avg_indexes):
        #draw graph
        self.ax.scatter(seg_indexes, seg_times, s=10, c=self.theme.scatter_color, alpha=0.3)
        self.ax.plot(avg_indexes, avg_times, linewidth=1.5, c=self.theme.plot_color)

        #set ticks
        interval_times = self.lsd.get_dynamic_interval(seg_times, ticks=9, format='%M:%S')
        self.ax.set_yticks(interval_times)
        self.ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

        #set headers
        self.set_axes_headers(title=f"{self.split_name} Time Over Attempts", title_color=self.theme.title_color)

        #labels
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Split Time")
        self.ax.set_axisbelow(True)

        self.seg_times = seg_times

        return self.fig

    def attempts_over_time(self):
        AOT_dates = self.lsd.AOT_dates
        AOT_attempts = self.lsd.AOT_attempts

        self.ax.plot(AOT_dates, AOT_attempts, c=self.theme.plot_color)
        
        interval_dates = self.lsd.get_dynamic_interval(AOT_dates, ticks=6, format='%Y-%m-%d')
        self.ax.set_xticks(interval_dates)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b. %d '%y"))

        self.set_axes_headers(title="Attempts Over Time", title_color=self.theme.title_color)
        
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Attempts")
        self.ax.set_axisbelow(True)

        return self.fig

    def imp_over_attempts(self):
        completed_times = self.lsd.finished_times
        abs_indexes = self.lsd.finished_indexes

        self.ax.plot(abs_indexes, completed_times, c=self.theme.plot_color, linewidth=1.5)

        interval_times = self.lsd.get_dynamic_interval(completed_times, ticks=16, format='%H:%M:%S')
        self.ax.set_yticks(interval_times)
        self.ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        self.set_axes_headers(title="Improvement Over Attempts", title_color=self.theme.title_color)
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig

    def imp_over_time(self):
        finished_dates = self.lsd.finished_dates
        finished_times = self.lsd.finished_times
        interval_dates = self.lsd.get_dynamic_interval(finished_times, ticks=16, format='%H:%M:%S')

        self.ax.scatter(finished_dates, finished_times, c=self.theme.scatter_color, s=5, alpha=1)

        #intervals
        interval_dates = self.lsd.get_dynamic_interval(finished_times, ticks=16, format='%H:%M:%S')
        self.ax.fill_between(finished_dates, min(interval_dates), finished_times, facecolor=self.theme.scatter_color, alpha=0.5)
        self.ax.set_yticks(interval_dates)
        self.ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        interval_dates = self.lsd.get_dynamic_interval(finished_dates, ticks=6, format='%Y-%m-%d')
        self.ax.set_xticks(interval_dates)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b. %d '%y"))

        self.set_axes_headers(title="Improvement Over Time", title_color=self.theme.title_color)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig

    def finished_runs_over_time(self):
        num_finished_runs = self.lsd.get_category_rel_indexes()
        finished_dates = self.lsd.finished_dates
        interval_dates = self.lsd.get_dynamic_interval(finished_dates, ticks=6, 
        format='%Y-%m-%d')

        self.ax.plot(finished_dates, num_finished_runs, c=self.theme.plot_color, linewidth=1.5)

        self.ax.set_xticks(interval_dates)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b. %d '%y"))

        self.set_axes_headers(title="Finished Runs Over Time", title_color=self.theme.title_color)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Finished Runs")
        self.ax.set_axisbelow(True)

        return self.fig

    def personal_best_over_time(self):
        """
        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
        """

        pb_dates = self.lsd.pb_dates
        pb_times = self.lsd.pb_times
        interval_dates = self.lsd.get_dynamic_interval(pb_times, ticks=16, format='%H:%M:%S')

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

        #intervals
        interval_times = self.lsd.get_dynamic_interval(pb_times, ticks=16, format='%H:%M:%S')

        self.ax.set_yticks(interval_times)
        self.ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        interval_dates = self.lsd.get_dynamic_interval(pb_dates, ticks=6, format='%Y-%m-%d')
        self.ax.set_xticks(interval_dates)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b. %d '%y"))

        self.set_axes_headers(title="Personal Best Over Time", title_color=self.theme.title_color)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)

        return self.fig
    
    def personal_best_over_attempts(self):
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


        interval_times = self.lsd.get_dynamic_interval(pb_times, ticks=16, format='%H:%M:%S')
        self.ax.set_yticks(interval_times)
        self.ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        self.set_axes_headers(title="Personal Best Over Attempts", title_color=self.theme.title_color)
        self.ax.set_xlabel("Attempts")
        self.ax.set_ylabel("Run Time")
        self.ax.set_axisbelow(True)


        return self.fig

    def hover_plot(self, event: MouseEvent, type_graph):
        """
        Check when hovering over a plot line, proceed to update the annotation.

        Depending on the `type_graph` different update functions are called. This is because 
        different graphs require different annotations with different data types.
        """

        plot_data: list[Line2D] = self.ax.get_lines()
        if event.inaxes != self.ax or len(plot_data) < 1:
            return

        line = plot_data[0]
        hovering_over_line, pointlist = line.contains(event)

        if hovering_over_line:
            match type_graph:
                case "Attempts Over Time":
                    self.update_attempts_over_time_annot(pointlist, line)
                case "PB Over Time":
                    self.update_pb_over_time_annot(pointlist, line)
                case "PB Over Attempts":
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

        # check for first index
        total_attempts_previous_session = line.get_ydata()[index-1]
        if index == 0:
            total_attempts_previous_session = 0
        daily_attempts = total_attempts - total_attempts_previous_session

        # set coordinates for annotation object relative to object being annotated
        pos = line.get_xydata()[index]
        self.annot.xy = pos

        self.annot.set_text(f"Total: {total_attempts}\nDaily: {daily_attempts}\nDate: {day}")

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
        if remaining_seconds != 0:
            formatted_str += f"{remaining_seconds}.{str(td.microseconds)[:1]}s "

        return formatted_str