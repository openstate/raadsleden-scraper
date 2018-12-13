import pandas as pd
import json

class OpenResultFile:
    def __init__(self):
        data = self.open_file('./pickles/files/sitemap_01903.json')
        self.print_data(data)

    @staticmethod
    def open_file(path):
        with open(path) as f:
            data = json.load(f)
        f.close()
        mapping = data.get('mapping')
        return [{'url': entry.get('url'), 'df': pd.read_json(entry.get('df'))} for entry in mapping]

    def print_data(self, result_array,):
        for entry in result_array:
            print(entry.get('url'))
            print(entry.get('df').to_string())


if __name__ == "__main__":
    OpenResultFile()