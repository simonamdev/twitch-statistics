import os
from pprint import pprint


class ApplicationLogParser:
    def __init__(self, file_path='', verbose=False):
        self.file_path = file_path
        self.split_rows = []
        self.log_data = []
        self.ip_addresses = []
        self.access_list = []
        self.unique_ip_count = 0
        self.serve_times = []
        self.max_serve_time = 0.0
        self.average_serve_time = 0.0
        self.routes_dict = {}
        self.verbose = verbose
        # Get the data from the log file and parse it
        self.retrieve_data_rows()
        self.parse_data_rows()

    def print(self, print_string=''):
        if self.verbose and not print_string == '':
            print('[LOG] {}'.format(print_string))

    def retrieve_data_rows(self):
        self.print('Retrieving data for parsing')
        with open(self.file_path, 'r') as log_file:
            # strip the new lines from every row
            for line in log_file:
                self.split_rows.append(line.strip().split('|'))
        self.print('{} rows recovered'.format(len(self.split_rows)))

    def get_data_rows(self):
        return self.split_rows

    def parse_data_rows(self):
        self.parse_ip_addresses()
        self.parse_serve_times()
        self.parse_route_popularity()

    def parse_ip_addresses(self):
        for line in self.split_rows:
            self.access_list.append([int(line[0]), line[2]])
            if line[2] not in self.ip_addresses:
                self.ip_addresses.append(line[2])
        self.unique_ip_count = len(self.ip_addresses)
        self.print('{} unique IP addresses found'.format(self.unique_ip_count))

    def parse_serve_times(self):
        for line in self.split_rows:
            # ignore "instant" pages (pages without database polls)
            if not line[1] == '0' or line[1] == '0.0':
                self.serve_times.append(round(float(line[1]), 4))
        self.max_serve_time = max(self.serve_times)
        self.average_serve_time = round(sum(self.serve_times) / len(self.serve_times), 4)
        self.print('Max serve time: {}s Average serve time: {}s'.format(self.max_serve_time, self.average_serve_time))

    def get_serve_time_dict(self):
        return {
            'serve_time_list': sorted(self.serve_times),
            'serve_time_average': self.average_serve_time,
            'serve_time_max': self.max_serve_time,
            'serve_time_median': sorted(self.serve_times)[len(self.serve_times) // 2]
        }

    def parse_route_popularity(self):
        for line in self.split_rows:
            try:
                self.routes_dict[line[3]]
            except KeyError:
                self.routes_dict[line[3]] = {
                    'params_dict': {}
                }
            else:
                try:
                    self.routes_dict[line[3]]['params_dict'][line[4]]
                except KeyError:
                    self.routes_dict[line[3]]['params_dict'][line[4]] = {
                        'count': 1,
                        'times': [line[0]]
                    }
                else:
                    self.routes_dict[line[3]]['params_dict'][line[4]]['count'] += 1
                    self.routes_dict[line[3]]['params_dict'][line[4]]['times'].append(line[0])
        # pprint(self.routes_dict)


def main():
    parser = ApplicationLogParser(os.path.join(os.getcwd(), 'logs', 'application.log'))

if __name__ == '__main__':
    main()
