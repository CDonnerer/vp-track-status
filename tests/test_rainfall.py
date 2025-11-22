"""Tests for rainfall data fetching."""

from unittest.mock import Mock, patch

from vp_track_status.rainfall import fetch_rainfall_data


def test_fetch_rainfall_data():
    mock_measures_response = Mock()
    mock_measures_response.json.return_value = {
        "items": [{"@id": "http://example.com/measure/123"}]
    }
    mock_measures_response.raise_for_status = Mock()

    mock_readings_response = Mock()
    mock_readings_response.json.return_value = {
        "items": [
            {"dateTime": "2024-01-01T00:00:00Z", "value": 5.0},
            {"dateTime": "2024-01-02T00:00:00Z", "value": 10.0},
        ]
    }
    mock_readings_response.raise_for_status = Mock()

    with patch("vp_track_status.rainfall.requests.get") as mock_get:
        mock_get.side_effect = [
            mock_measures_response,
            mock_readings_response,
            mock_readings_response,
        ]

        df = fetch_rainfall_data("239374TP", "2024-01-01", "2024-01-02")

        assert len(df) == 2
        assert "dateTime" in df.columns
        assert "value" in df.columns
