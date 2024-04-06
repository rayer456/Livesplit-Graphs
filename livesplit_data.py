import datetime
import gc
from dateutil import relativedelta
import xml.etree.ElementTree as ET
from statistics import pstdev, mean

import variables


class LiveSplitData():
    def __init__(self, path: str):
        self.set_XML_root(path)
        self.set_segments()
        self.set_game_name()
        self.set_game_category()
        self.set_variables()
        self.set_split_names()
        self.extract_category_data()
        self.set_available_variables()

    def set_XML_root(self, path):
        xtree = ET.parse(path)
        self.xroot = xtree.getroot()

    def set_segments(self):
        self.segments = self.xroot.find('Segments')

    def set_available_variables(self):
        self.available_variables = variables.get_category_variables(self.game_name, self.game_category)
 
    def set_game_name(self):
        self.game_name = self.xroot.find('GameName').text
    
    def set_game_category(self):
        self.game_category = self.xroot.find('CategoryName').text
    
    def set_variables(self):
        self.variables = self.xroot.find('Metadata').find('Variables')
    
    def set_split_names(self):
        self.split_names = [segment.find('Name').text for segment in self.segments]

    def extract_category_data(self):
        ''' Extract necessary data to plot CATEGORY graphs
            - Finished Dates & Attempted Dates
            - Finished Times
            - Finished Indexes & Attempted Indexes
            -
        '''
        self.finished_dates, self.finished_times, self.finished_indexes = [], [], []

        for i, attempt in enumerate(self.xroot.find('AttemptHistory')):
            real_time = attempt.find('RealTime')
            end_date = attempt.attrib.get('ended')
            converted_date = datetime.datetime.strptime(end_date[:10], '%m/%d/%Y')
            if real_time is not None:
                self.finished_dates.append(converted_date)
                t = real_time.text
                self.finished_times.append(datetime.datetime.strptime(t[:t.find('.')], '%H:%M:%S'))
                self.finished_indexes.append(i+1)
        
        self.AOT_dates, self.AOT_attempts = [], []

        attempt_history = self.xroot.find('AttemptHistory')
        start_dates = [attempt.attrib.get('started') for attempt in attempt_history]
        last_date = None

        for i, start_date in enumerate(start_dates):
            current_date = datetime.datetime.strptime(start_date[:10], '%m/%d/%Y')
            #initial
            if last_date is None:
                last_date = current_date
            
            #different day?
            if current_date != last_date:
                self.AOT_dates.append(last_date)
                self.AOT_attempts.append(i)

            #last date
            if i+1 == len(start_dates):
                self.AOT_dates.append(current_date)
                self.AOT_attempts.append(i+1)
            
            last_date = current_date

    def get_category_rel_indexes(self):
        return [i+1 for i in range(len(self.finished_indexes))]
    
    def extract_segment_data(self, split_name):
        ''' Extracts following data with and without outliers:
            - Segment Times
            - Segment Indexes
            - Average Segment Time every 10 times
            - Index for that Average Segment Time
        '''
        gc.collect()
        self.seg_times, self.seg_indexes = [], []
        
        for segment in self.segments:
            if segment.find('Name').text == split_name:
                seg_history = segment.find('SegmentHistory')
                for attempt in seg_history:
                    try:
                        index = int(attempt.attrib.get('id'))
                        if index > 0:
                            t = attempt[0].text #index error

                            #add missing microseconds
                            if len(t) == 8:
                                t += ".0000100"
                            
                            #0:03:33.2988750
                            td_time = datetime.timedelta(
                            minutes=int(t[t.find(':')+1:t.find(':', 3)]), 
                            seconds=int(t[t.find(':', 3)+1:t.find('.')]), 
                            microseconds=int(t[t.find('.')+1:-1])
                            )

                            dt_time = datetime.datetime.strptime(str(td_time), '%H:%M:%S.%f')
                            self.seg_times.append(dt_time)

                    except ValueError:
                        print("value_error")
                        continue
                    except IndexError:
                        #empty Time element
                        continue
                break

        self.seg_indexes = [i for i in range(1, len(self.seg_times)+1)]
        self.avg_seg_times, self.avg_seg_indexes = self.get_averages(self.seg_times)
        
    def get_averages(self, seg_times) -> tuple:
        avg_times, avg_indexes = [], []
        start, end = 0, 10

        while end < len(seg_times):
            selection = seg_times[start:end]
            avg_times.append(self.get_avg_HMS(selection))
            avg_indexes.append(end)

            start = end
            end += 10
        return avg_times, avg_indexes
    
    def get_avg_HMS(self, values: list):
        '''
        Returns datetime object of average time\n
        values should be a list of datetime objects
        '''
        total = datetime.timedelta(seconds=0)
        for time in values:
            total_seconds = time.hour * 3600 + time.minute * 60 + time.second
            total += datetime.timedelta(seconds=total_seconds)

        return datetime.datetime(1900, 1, 1, 0, 0, 0) + total / len(values)
    
    def get_dynamic_interval(self, realtimes, ticks, format: str):
        '''formats: %M:%S | %Y-%m-%d | %H:%M:%S'''
        ticks -= 1
        sorted_realtimes = sorted(realtimes)

        if format == '%M:%S':
            #5:26.20 -> 5:26.00
            start_time = sorted_realtimes[0].replace(microsecond=0)
            #5:30.40 -> 5:31.00
            end_time = (sorted_realtimes[-1] + relativedelta.relativedelta(seconds=1)).replace(microsecond=0)
        
        elif format == '%Y-%m-%d':
            start_date = sorted_realtimes[0].replace(day=1)
            end_date = sorted_realtimes[-1].replace(day=1) + relativedelta.relativedelta(months=1)

            time_delta = relativedelta.relativedelta(end_date, start_date)

            time_delta_months = time_delta.months
            time_delta_months += time_delta.years * 12
            
            interval = time_delta_months / ticks
            if interval < 1:
                interval = 1
                ticks =  time_delta_months

            base_time = start_date
            interval_dates = [base_time]
            i = 0
            while i < ticks:
                base_time = base_time + relativedelta.relativedelta(months=round(interval))
                interval_dates.append(base_time)
                i += 1
            return interval_dates
        
        elif format == '%H:%M:%S':
            start_time = sorted_realtimes[0].replace(second=0)
            end_time = (sorted_realtimes[-1] + relativedelta.relativedelta(minutes=1)).replace(second=0)

        #M:S and H:M:S
        #example: 5 seconds delta
        time_delta = relativedelta.relativedelta(end_time, start_time)

        time_delta_seconds = time_delta.seconds
        time_delta_seconds += time_delta.minutes * 60
        time_delta_seconds += time_delta.hours * 3600

        interval = time_delta_seconds / ticks

        if interval < 1:
            interval = 1
            ticks = time_delta_seconds
        
        base_time = start_time
        interval_dates = [base_time]
        for i in range(ticks):
            base_time += relativedelta.relativedelta(seconds=round(interval))
            interval_dates.append(base_time)

        return interval_dates
    
    def remove_segment_outliers(self):
        times_in_seconds = []
        for time in self.seg_times:
            hours_in_seconds = time.hour * 3600
            minutes_in_seconds = time.minute * 60
            seconds = time.second
            milliseconds = float(f"0.{datetime.datetime.strftime(time, format='%f')}")
            
            times_in_seconds.append(hours_in_seconds + minutes_in_seconds + seconds + milliseconds)

        std_dev = pstdev(times_in_seconds)
        n_mean = mean(times_in_seconds)
        upper_limit = n_mean + std_dev * 3

        self.seg_times_NO = [datetime.datetime(1900, 1, 1) + relativedelta.relativedelta(seconds=time) for time in times_in_seconds if time < upper_limit]
        
        self.seg_indexes_NO = [i for i in range(1, len(self.seg_times_NO)+1)]

        self.avg_seg_times_NO, self.avg_seg_indexes_NO = self.get_averages(self.seg_times_NO)