import os
from pprint import pprint


class ApplicationLogParser:
    def __init__(self, file_path=''):
        self.file_path = file_path
        self.split_rows = []
        self.log_data = []
        self.ip_addresses = []
        self.serve_times = []
        self.max_serve_time = 0.0
        self.average_serve_time = 0.0
        self.routes_dict = {}

    def get_data_rows(self):
        with open(self.file_path, 'r') as log_file:
            # strip the new lines from every row
            for line in log_file:
                self.split_rows.append(line.strip().split('|'))

    def parse_data_rows(self):
        pprint(self.split_rows)
        self.parse_ip_addresses()
        self.parse_serve_times()
        self.parse_route_popularity()

    def parse_ip_addresses(self):
        for line in self.split_rows:
            if line[2] not in self.ip_addresses:
                self.ip_addresses.append(line[2])

    def parse_serve_times(self):
        for line in self.split_rows:
            # ignore "instant" pages (pages without database polls)
            if not line[1] == '0' or line[1] == '0.0':
                self.serve_times.append(float(line[1]))
        self.max_serve_time = max(self.serve_times)
        self.average_serve_time = sum(self.serve_times) / len(self.serve_times)

    def parse_route_popularity(self):
        for line in self.split_rows:
            route_dict = {
                'name': line[3],
                'params': line[4],
                'count': 1
            }
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
                        'count': 1
                    }
                else:
                    self.routes_dict[line[3]]['params_dict'][line[4]]['count'] += 1
        pprint(self.routes_dict)


def main():
    parser = ApplicationLogParser(os.path.join(os.getcwd(), 'logs', 'application.log'))
    parser.get_data_rows()
    parser.parse_data_rows()

if __name__ == '__main__':
    main()
