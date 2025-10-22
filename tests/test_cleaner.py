import pytest
import os
from src.cleaner import map_csv_to_tsv_columns

class TestMapCSVToCSV:
    
    # 1) empty file path
    def test_empty_file_path(self):
        with pytest.raises(ValueError, match="CSV file path cannot be empty"):
            map_csv_to_tsv_columns('')
            
    # 2) non-existent file
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            map_csv_to_tsv_columns('nonexistent_file.csv')
            
    # 3) empty CSV file
    def test_empty_csv(self):
        with pytest.raises(IOError, match="file is empty"):
            map_csv_to_tsv_columns('tests/test_data/empty.csv')
    
    # 4) CSV with no headers
    def test_no_headers(self):
        with pytest.raises(ValueError, match="no headers"):
            map_csv_to_tsv_columns('tests/test_data/no_headers.csv')
            
    # 5) valid CSV with exact matches
    def test_exact_match(self):
        result = map_csv_to_tsv_columns('tests/test_data/exact_match.csv')
        
        assert result is not None
        assert isinstance(result, dict)
        
        assert 'EVENT_ID' in result
        assert result['EVENT_ID'] == 'EVENT_ID'
        
    # 6) case-insensitive matching
    def test_case_insensitive_match(self):
        result = map_csv_to_tsv_columns('tests/test_data/mixed_case.csv')
        
        # if CSV has "event_id" it should match TSV "EVENT_ID"
        assert result['EVENT_ID'] is not None
    
    # 7) synonym matching
    def test_synonym_match(self):
        result = map_csv_to_tsv_columns('tests/test_data/synonym_test.csv')
        
        # if CSV has "zip code" it should match TSV "POSTAL_CODE" via synonyms
        assert result.get('POSTAL_CODE') == 'zip code'
        
    # 8) unmapped columns return None
    def test_unmapped_columns(self):
        result = map_csv_to_tsv_columns('tests/test_data/partial_match.csv')
        
        # should have some None values for columns that don't match
        assert None in result.values()
        
    # 9) no duplicate mappings
    def test_no_duplicate_mappings(self):
        """Test that same CSV column isn't mapped to multiple TSV columns"""
        result = map_csv_to_tsv_columns('tests/test_data/exact_match.csv')
        
        # get all non-None mapped values
        mapped_values = [v for v in result.values() if v is not None]
        
        # check no duplicates
        assert len(mapped_values) == len(set(mapped_values)), "Same CSV column mapped multiple times"
        
    # 10) all TSV columns present in result
    def test_all_tsv_columns_in_result(self):
        """Test that result contains all TSV column keys"""
        result = map_csv_to_tsv_columns('tests/test_data/exact_match.csv')
        
        expected_keys = [
            'EVENT_ID', 'SESSION_ID', 'AGE', 'GRADE', 'ORG_ID', 
            'GENDER_ID', 'ETHNICITY_ID', 'STUDENT_CODE', 'POSTAL_CODE',
            'IS_RETURNING_STUDENT_FLAG', 'STUDENT_FIRST_NAME', 'STUDENT_LAST_NAME'
        ]
        
        for key in expected_keys:
            assert key in result
    
    # 11) CSV with empty column headers (warning test)
    def test_empty_column_headers_warning(self, capsys):
        """Test that empty CSV column headers produce a warning"""
        result = map_csv_to_tsv_columns('tests/test_data/empty_columns.csv')
        
        captured = capsys.readouterr()
        assert "Warning: CSV contains empty column headers" in captured.out
    
    # 12) synonym file missing
    def test_missing_synonym_file(self, capsys, monkeypatch):
        """Test that missing synonym file doesn't crash, just warns"""
        # Mock load_column_synonyms to raise FileNotFoundError
        def mock_load():
            raise FileNotFoundError("Synonym file not found")
        
        monkeypatch.setattr('src.cleaner.load_column_synonyms', mock_load)
        
        result = map_csv_to_tsv_columns('tests/test_data/exact_match.csv')
        
        captured = capsys.readouterr()
        assert "WARNING: Could not load synonyms" in captured.out
        assert result is not None  # Should still return a result