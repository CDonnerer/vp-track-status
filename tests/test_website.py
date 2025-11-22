"""Tests for website generation."""

from datetime import date

from vp_track_status.website import generate_html


def test_generate_html(sample_rainfall_data):
    prediction_result = {
        "date": date(2024, 1, 3),
        "prediction": 0,
        "prediction_label": "Dry",
        "features": {
            "rain_1d": 2.0,
            "rain_2d": 12.0,
            "rain_3d": 17.0,
            "rain_5d": 17.0,
            "rain_7d": 17.0,
        },
    }

    html = generate_html(prediction_result, sample_rainfall_data)

    assert isinstance(html, str)
    assert len(html) > 0
    assert "<!DOCTYPE html>" in html
