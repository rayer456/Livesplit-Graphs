import datetime
from dateutil import relativedelta
import xml.etree.ElementTree as ET
from statistics import pstdev, mean
import pandas as pd
from time import perf_counter

import variables


class LiveSplitData():
    avg_segment_times: pd.DataFrame
    segment_times: pd.DataFrame
    
    def __init__(self, path: str):
        start = perf_counter()
        self.set_XML_root(path)
        self.segments = self.xroot.find('Segments')
        self.game_name = self.xroot.find('GameName').text
        self.game_category = self.xroot.find('CategoryName').text
        self.variables = self.xroot.find('Metadata').find('Variables')
        self.split_names = [segment.find('Name').text for segment in self.segments]
        self.available_variables = variables.get_category_variables(self.game_name, self.game_category)

        self.extract_category_data()
        
        end = perf_counter()
        # print(end-start)

    def set_XML_root(self, path):
        xtree = ET.parse(path)
        self.xroot = xtree.getroot()
        
    def extract_category_data(self):
        ''' Extract necessary data to plot CATEGORY graphs
            - Finished Dates & Attempted Dates
            - Finished Times
            - Finished Indexes & Attempted Indexes
            -
        '''
        self.finished_dates, self.finished_times, self.finished_indexes = [], [], []
        self.pb_dates, self.pb_times = [], []
        self.pb_abs_indexes = []
        self.finished_attempts = []
        self.unique_finished_dates = []

        pb_time = datetime.datetime.strptime("23:59:59", "%H:%M:%S")
        last_date = None
        finished_counter = 0
        for i, attempt in enumerate(self.xroot.find('AttemptHistory')):
            real_time = attempt.find('RealTime')
            if real_time is None: # if run not finished
                continue

            finished_date = datetime.datetime.strptime(attempt.attrib.get('ended')[:10], '%m/%d/%Y')
            finished_counter += 1
            if last_date is None:
                last_date = finished_date

            # update counter if same day
            if finished_date == last_date and len(self.finished_attempts) != 0:
                self.finished_attempts[-1] = finished_counter

            # first attempt or different date
            else:
                self.unique_finished_dates.append(finished_date)
                self.finished_attempts.append(finished_counter)

            self.finished_dates.append(finished_date)

            last_date = finished_date

            t = real_time.text
            if len(t) == 8:
                    t += ".0000100"
            finished_time = datetime.datetime.strptime(t[:-1], '%H:%M:%S.%f')
            self.finished_times.append(finished_time)
            self.finished_indexes.append(i+1)

            # check if PB
            if finished_time < pb_time:
                self.pb_dates.append(finished_date)
                self.pb_times.append(finished_time)
                pb_time = finished_time
                self.pb_abs_indexes.append(i+1)
                # TODO this can crash
                self.pb_id = int(attempt.attrib.get('id'))


        self.AOT_dates, self.AOT_attempts, self.daily_time_played = [], [], []
        attempt_history = self.xroot.find('AttemptHistory')
        current_dates = [datetime.datetime.strptime(attempt.attrib.get('ended')[:10], '%m/%d/%Y') for attempt in attempt_history]
        time_played = [datetime.datetime.strptime(attempt.attrib.get('ended'), '%m/%d/%Y %H:%M:%S') - datetime.datetime.strptime(attempt.attrib.get('started'), '%m/%d/%Y %H:%M:%S') for attempt in attempt_history]
        total_daily_playtime = relativedelta.relativedelta(hour=0)
        last_date = None
        for i, current_date in enumerate(current_dates):
            # initial avoid issues with NoneType
            if last_date is None:
                last_date = current_date
            
            # different day?
            if current_date != last_date:
                self.AOT_dates.append(last_date)
                self.AOT_attempts.append(i)
                self.daily_time_played.append(total_daily_playtime)
                total_daily_playtime = relativedelta.relativedelta(hour=0)

            # final attempt
            if i+1 == len(current_dates):
                self.AOT_dates.append(current_date)
                self.AOT_attempts.append(i+1)

                # update total now since it's the last cycle
                time_in_attempt = time_played[i]
                total_daily_playtime += time_in_attempt
                self.daily_time_played.append(total_daily_playtime)
            
            last_date = current_date
            time_in_attempt = time_played[i]
            total_daily_playtime += time_in_attempt
        
        xm = pd.DataFrame({
            "dates": self.AOT_dates,
            "attempts": self.AOT_attempts,
        })
    
    def extract_segment_data(self, segment_index: int, show_outliers: bool):
        ''' Extracts following data with and without outliers:
            - Segment Times
            - Segment Indexes
            - Average Segment Time every 10 times
            - Index for that Average Segment Time
        '''
        seg_times = []
        self.from_pb = []
        attempt_ids = []
        
        segment = self.segments[segment_index]
        segment_history = segment.find('SegmentHistory')
        for attempt in segment_history:
            try:
                attempt_id = int(attempt.attrib.get('id'))
                if attempt_id < 0:
                    continue

                # TODO add support for GameTime (no)
                time_type = "RealTime"
                try:
                    t: str = attempt.find(time_type).text
                except AttributeError:
                    # can't find RealTime element
                    continue

                # add missing microseconds
                if len(t) == 8:
                    t += ".0000100"
                
                # remove last digit for microseconds as datetime.strptime() only allows up to 6 decimals after the decimal point, livesplit stores 7 at most
                dt_time = datetime.datetime.strptime(t[:-1], '%H:%M:%S.%f')
                seg_times.append(dt_time)

                if attempt_id == self.pb_id:
                    self.from_pb.append(True)
                else:
                    self.from_pb.append(False)

                attempt_ids.append(attempt_id)

            except ValueError as e:
                print(e)
                continue
            except IndexError:
                #empty Time element
                continue

        self.avg_segment_times = self.get_averages(seg_times)

        self.segment_times = pd.DataFrame({
            'seg_times': seg_times,
            'is_from_pb': self.from_pb,
            'attempt_ids': attempt_ids,
        })

        if not show_outliers:
            self.remove_segment_outliers()
        
    def get_averages(self, seg_times) -> pd.DataFrame:
        avg_times, avg_indexes = [], []
        start, end = 0, 10

        while end < len(seg_times):
            selection = seg_times[start:end]
            avg_times.append(self.get_avg_HMS(selection))
            avg_indexes.append(end)

            start = end
            end += 10
            
        return pd.DataFrame({
            'avg_times': avg_times,
            'avg_indexes': avg_indexes,
        })
    
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
    
    def get_dynamic_interval(self, realtimes: list[datetime.datetime], ticks, format: str):
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
    
    def convert_datetime_to_float(self, time: datetime.datetime) -> float:
        hours_in_seconds = time.hour * 3600
        minutes_in_seconds = time.minute * 60
        seconds = time.second
        milliseconds = float(f"0.{datetime.datetime.strftime(time, format='%f')}")
        
        result = hours_in_seconds + minutes_in_seconds + seconds + milliseconds
        return result

    def remove_segment_outliers(self):
        times_in_seconds = [self.convert_datetime_to_float(row['seg_times']) for _, row in self.segment_times.iterrows()]

        # remove row if outlier
        upper_limit = mean(times_in_seconds) + pstdev(times_in_seconds) * 3
        for index, row in self.segment_times.iterrows():
            time = self.convert_datetime_to_float(row['seg_times'])
            if time > upper_limit:
                self.segment_times.drop(index, inplace=True)
        
        # refresh index 
        self.segment_times.index = range(len(self.segment_times))

        self.avg_segment_times = self.get_averages(self.segment_times["seg_times"])