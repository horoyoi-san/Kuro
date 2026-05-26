from timeline_utils import bangkok_datetime, run_timeline


CONFIG = {
    "game_name": "Wuthering Waves",
    "start_dates": {
        "Drip": bangkok_datetime(2026, 3, 25, 11, 0),
        "Beta CN": bangkok_datetime(2026, 3, 28, 17, 0),
        "Beta OS": bangkok_datetime(2026, 4, 4, 17, 0),
        "Release": bangkok_datetime(2026, 4, 30, 10, 0),
    },
    "intervals": {
        "Drip": 42,
        "Beta CN": 42,
        "Beta OS": 42,
        "Release": 42,
    },
    "start_version": 3.3,
    "end_version": 8.0,
    "output_file": "data/wuwa.txt",
    "bullet": True,
}


if __name__ == "__main__":
    run_timeline(CONFIG)
