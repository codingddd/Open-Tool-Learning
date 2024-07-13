from ..utils import read_JSON, write_JSON

import json


class General_dataset:
    def __init__(self, filename, write_filename="", template="default"):
        self.filename = filename
        self.write_filename = write_filename
        self.template = template
        self.data = []
        self.load_data()

    def load_data(self):
        self.data = read_JSON(self.filename)

    # rewrite according to dataset you need to handle,I cut each assistant into the input and output of the model.


if __name__ == "__main__":
    print("dsadas")
