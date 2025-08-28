from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from cleaner import readCSV

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STEAM:CODERS Data Automation Tool")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # upload button
        self.upload_button = QPushButton("Upload CSV")
        self.upload_button.clicked.connect(self.load_csv)
        layout.addWidget(self.upload_button)
        
        # table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def load_csv(self):
        print("load_csv called")
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV FIles (*.csv)")
        if not file_path:
            return
        
        # use readCSV method from cleaner
        data = readCSV(file_path)
        if not data:
            return
        
        # first row is headers
        headers = data[0]
        rows = data[1:]
        print(f"rows read from CSV: {len(rows)}")
        #FIXME table is displaying 125 rows instead of 18
        self.table.clear()                # clears contents + headers
        self.table.setRowCount(0)         # reset rows
        self.table.setColumnCount(0)      # reset columns
        
        # set items
        for row_ind, row in enumerate(rows):
            for col_ind, val in enumerate(row):
                self.table.setItem(row_ind, col_ind, QTableWidgetItem(val))