from timeline_utils import bangkok_datetime, run_timeline


CONFIG = {
    "game_name": "Wuthering Waves",
    "start_dates": {
        "Drip": bangkok_datetime(2025, 7, 29, 11, 0),
        "Beta": bangkok_datetime(2025, 8, 7, 17, 0),
        "Release": bangkok_datetime(2025, 8, 28, 10, 0),
    },
    "intervals": {
        "Drip": 42,
        "Beta": 42,
        "Release": 42,
    },
    "start_version": 2.6,
    "end_version": 8.0,
    "output_file": "data/wuwa_legacy.txt",
}


if __name__ == "__main__":
    run_timeline(CONFIG)
