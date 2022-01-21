import pandas as pd


class InputDataSetCSV(object):
    def __init__(self, inputFilename, init=None, end=None):
        self.inputFilename = inputFilename
        self.dataset = self._obtain_dataset()
        self.init = init
        if init is None:
            self.init = 0
        self.end = end
        if end is None:
            self.end = len(self.dataset)

    def _obtain_dataset(self):
        csv_file = pd.read_csv(
            self.inputFilename, header=0, sep=",", quotechar='"', encoding="utf-8"
        )
        return csv_file.values.tolist()
