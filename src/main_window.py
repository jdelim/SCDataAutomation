from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QDialog, 
    QDialogButtonBox, QMessageBox, QSplitter, QGroupBox
)
from PySide6.QtCore import Qt
from cleaner import *
import copy

class ColumnMappingDialog(QDialog):
    """Dialog for manually mapping unmapped columns."""
    def __init__(self, unmapped_columns, csv_headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Columns Manually")
        self.setModal(True)
        self.resize(500, 400)
        
        self.unmapped_columns = unmapped_columns
        self.csv_headers = csv_headers
        self.mappings = {}
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Some columns could not be automatically mapped.\n"
            "Please select which CSV column corresponds to each TSV column:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Create dropdown for each unmapped column
        self.combo_boxes = {}
        for tsv_col in unmapped_columns:
            group = QGroupBox(f"TSV Column: {tsv_col}")
            group_layout = QVBoxLayout()
            
            combo = QComboBox()
            combo.addItem("-- Skip this column --")
            combo.addItems(csv_headers)
            
            group_layout.addWidget(QLabel("Select matching CSV column:"))
            group_layout.addWidget(combo)
            group.setLayout(group_layout)
            
            layout.addWidget(group)
            self.combo_boxes[tsv_col] = combo
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_mappings(self):
        """Returns the user's column mappings."""
        mappings = {}
        for tsv_col, combo in self.combo_boxes.items():
            selected = combo.currentText()
            if selected != "-- Skip this column --":
                mappings[tsv_col] = selected
            else:
                mappings[tsv_col] = None
        return mappings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STEAM:CODERS Data Automation Tool")
        self.resize(1400, 800)
        
        # Data storage
        self.csv_file_path = None
        self.raw_data = None
        self.cleaned_data = None
        self.column_mapping = None
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.upload_button = QPushButton("1. Upload CSV")
        self.upload_button.clicked.connect(self.upload_csv)
        button_layout.addWidget(self.upload_button)
        
        self.clean_button = QPushButton("2. Clean CSV")
        self.clean_button.clicked.connect(self.clean_csv)
        self.clean_button.setEnabled(False)
        button_layout.addWidget(self.clean_button)
        
        self.export_button = QPushButton("3. Export to TSV")
        self.export_button.clicked.connect(self.export_to_tsv)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Please upload a CSV file to begin.")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)
        
        # Splitter for side-by-side tables
        splitter = QSplitter(Qt.Horizontal)
        
        # Raw data table
        raw_group = QGroupBox("Raw CSV Data")
        raw_layout = QVBoxLayout()
        self.raw_table = QTableWidget()
        raw_layout.addWidget(self.raw_table)
        raw_group.setLayout(raw_layout)
        splitter.addWidget(raw_group)
        
        # Cleaned data table
        cleaned_group = QGroupBox("Cleaned Data (Preview)")
        cleaned_layout = QVBoxLayout()
        self.cleaned_table = QTableWidget()
        cleaned_layout.addWidget(self.cleaned_table)
        cleaned_group.setLayout(cleaned_layout)
        splitter.addWidget(cleaned_group)
        
        main_layout.addWidget(splitter)
        
        # Central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def upload_csv(self):
        """Upload and display CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CSV", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return
        
        self.csv_file_path = file_path
        self.raw_data = readCSV(file_path)
        
        if not self.raw_data:
            QMessageBox.critical(self, "Error", "Failed to read CSV file!")
            return
        
        # Display raw data
        self.display_table(self.raw_table, self.raw_data)
        
        # Update UI state
        self.status_label.setText(f"✓ Loaded: {file_path} ({len(self.raw_data)-1} rows)")
        self.clean_button.setEnabled(True)
        self.cleaned_table.clear()
        self.cleaned_data = None
    
    def clean_csv(self):
        """Clean the CSV data."""
        if not self.raw_data:
            QMessageBox.warning(self, "Warning", "Please upload a CSV file first!")
            return
        
        self.status_label.setText("Cleaning data...")
        
        # Make a copy to clean
        self.cleaned_data = copy.deepcopy(self.raw_data)
        
        # Columns that need cleaning
        columns_to_clean = ['GENDER_ID', 'ETHNICITY_ID', 'ORG_ID']
        
        failed_columns = []
        for column_name in columns_to_clean:
            try:
                result = clean_column(column_name, self.cleaned_data)
                if result is None:
                    # Column not found automatically
                    failed_columns.append(column_name)
                else:
                    self.cleaned_data = result
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Cleaning Error", 
                    f"Error cleaning {column_name}: {str(e)}"
                )
        
        # Handle unmapped columns
        if failed_columns:
            csv_headers = self.raw_data[0]
            dialog = ColumnMappingDialog(failed_columns, csv_headers, self)
            
            if dialog.exec() == QDialog.Accepted:
                manual_mappings = dialog.get_mappings()
                
                # Clean columns with manual mappings
                for column_name in failed_columns:
                    csv_col = manual_mappings.get(column_name)
                    if csv_col:
                        # Temporarily modify headers to match
                        original_header = csv_headers[csv_headers.index(csv_col)]
                        csv_headers[csv_headers.index(csv_col)] = column_name
                        
                        result = clean_column(column_name, self.cleaned_data)
                        if result:
                            self.cleaned_data = result
                        
                        # Restore original header
                        csv_headers[csv_headers.index(column_name)] = original_header
            else:
                QMessageBox.information(
                    self,
                    "Cancelled",
                    "Column mapping cancelled. Data partially cleaned."
                )
        
        # Display cleaned data
        self.display_table(self.cleaned_table, self.cleaned_data)
        
        self.status_label.setText("✓ Data cleaned successfully!")
        self.export_button.setEnabled(True)
    
    def export_to_tsv(self):
        """Export cleaned data to TSV file."""
        if not self.cleaned_data:
            QMessageBox.warning(self, "Warning", "Please clean the CSV first!")
            return
        
        # Get save location
        tsv_path, _ = QFileDialog.getSaveFileName(
            self, "Save TSV", "", "TSV Files (*.tsv)"
        )
        if not tsv_path:
            return
        
        if not tsv_path.endswith('.tsv'):
            tsv_path += '.tsv'
        
        try:
            # Save cleaned data to temporary CSV
            temp_csv = self.csv_file_path.replace('.csv', '_cleaned_temp.csv')
            with open(temp_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(self.cleaned_data)
            
            # Map columns
            column_mapping = map_csv_to_tsv_columns(temp_csv)
            
            if not column_mapping:
                QMessageBox.critical(self, "Error", "Failed to map columns!")
                return
            
            # Transfer to TSV
            success = transfer_csv_to_tsv_with_mapping(
                temp_csv, tsv_path, column_mapping
            )
            
            # Clean up temp file
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Data exported successfully to:\n{tsv_path}"
                )
                self.status_label.setText(f"✓ Exported to: {tsv_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export TSV!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def display_table(self, table, data):
        """Display data in a table widget."""
        if not data:
            return
        
        headers = data[0]
        rows = data[1:]
        
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        
        for row_ind, row in enumerate(rows):
            for col_ind, val in enumerate(row):
                table.setItem(row_ind, col_ind, QTableWidgetItem(str(val)))
        
        table.resizeColumnsToContents()