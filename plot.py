from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.axes import Axes

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
        self.sc = self.ax.scatter(seg_indexes, seg_times, s=10, c=self.theme.scatter_color, alpha=0.3)
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

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(15,15),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)


        return self.fig

    def attempts_over_time(self):
        AOT_dates = self.lsd.AOT_dates
        AOT_attempts = self.lsd.AOT_attempts
        interval_dates = self.lsd.get_dynamic_interval(AOT_dates, ticks=6, format='%Y-%m-%d')

        self.ax.plot(AOT_dates, AOT_attempts, c=self.theme.plot_color)

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

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            print(f"{cont} {ind}")
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def update_annot(self, ind):
        pos = self.sc.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos

        attempt_num = ind["ind"][0] + 1
        formatted_time = self.seg_times[attempt_num-1].strftime("%M:%S.%f")[:9]
        self.annot.set_text(f"{attempt_num}\n{formatted_time}")

        self.annot.get_bbox_patch().set_facecolor("white")
        self.annot.get_bbox_patch().set_alpha(0.8)


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