from typing import Any, List

import pandas as pd


class OuputDataSetCSV:
    def __init__(self, outputFileName: str, columns: List[str]):
        self.outputFileName = outputFileName
        self.columns = columns
        self.dataset: List[List[Any]] = []

    def append(self, newrow: List[Any]) -> None:
        self.dataset.append(newrow)

    def save(self) -> None:
        df = pd.DataFrame(data=self.dataset, columns=self.columns)
        df.to_excel(
            self.outputFileName.replace(".csv", "") + ".xlsx",
            index=False,
            columns=self.columns,
        )
