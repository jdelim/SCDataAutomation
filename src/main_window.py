from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)
from cleaner import *

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
        
        # clean button
        self.clean_csv_button = QPushButton("Clean CSV")
        self.clean_csv_button.clicked.connect(self.load_clean_csv)
        layout.addWidget(self.clean_csv_button)
        
        # table widget
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def load_clean_csv(self): # FIXME cleaned values not displaying on table
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return
        
        # use readCSV method from cleaner
        data = readCSV(file_path)
        clean_data = data
        columns = ['gender', 'ethnicity', 'organization']
        
        for column in columns:
            clean_data = clean_column(column, clean_data)
        if not clean_data:
            return
        
        # first row is headers
        headers = clean_data[0]
        rows = clean_data[1:]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        
        # set items
        for row_ind, row in enumerate(rows):
            for col_ind, val in enumerate(row):
                self.table.setItem(row_ind, col_ind, QTableWidgetItem(val))        
    
    def load_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return
        
        # use readCSV method from cleaner
        data = readCSV(file_path)
        if not data:
            return
        
        # first row is headers
        headers = data[0]
        rows = data[1:]
        
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        
        # set items
        for row_ind, row in enumerate(rows):
            for col_ind, val in enumerate(row):
                self.table.setItem(row_ind, col_ind, QTableWidgetItem(val))