import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


BANGKOK_TZ = timezone(timedelta(hours=7))

DAY_NAMES_TH = [
    "\u0e08\u0e31\u0e19\u0e17\u0e23\u0e4c",
    "\u0e2d\u0e31\u0e07\u0e04\u0e32\u0e23",
    "\u0e1e\u0e38\u0e18",
    "\u0e1e\u0e24\u0e2b\u0e31\u0e2a\u0e1a\u0e14\u0e35",
    "\u0e28\u0e38\u0e01\u0e23\u0e4c",
    "\u0e40\u0e2a\u0e32\u0e23\u0e4c",
    "\u0e2d\u0e32\u0e17\u0e34\u0e15\u0e22\u0e4c",
]

MONTH_NAMES_TH = [
    "\u0e21\u0e01\u0e23\u0e32\u0e04\u0e21",
    "\u0e01\u0e38\u0e21\u0e20\u0e32\u0e1e\u0e31\u0e19\u0e18\u0e4c",
    "\u0e21\u0e35\u0e19\u0e32\u0e04\u0e21",
    "\u0e40\u0e21\u0e29\u0e32\u0e22\u0e19",
    "\u0e1e\u0e24\u0e29\u0e20\u0e32\u0e04\u0e21",
    "\u0e21\u0e34\u0e16\u0e38\u0e19\u0e32\u0e22\u0e19",
    "\u0e01\u0e23\u0e01\u0e0e\u0e32\u0e04\u0e21",
    "\u0e2a\u0e34\u0e07\u0e2b\u0e32\u0e04\u0e21",
    "\u0e01\u0e31\u0e19\u0e22\u0e32\u0e22\u0e19",
    "\u0e15\u0e38\u0e25\u0e32\u0e04\u0e21",
    "\u0e1e\u0e24\u0e28\u0e08\u0e34\u0e01\u0e32\u0e22\u0e19",
    "\u0e18\u0e31\u0e19\u0e27\u0e32\u0e04\u0e21",
]


def bangkok_datetime(year, month, day, hour=10, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=BANGKOK_TZ)


def format_date_th(dt):
    local_dt = dt.astimezone(BANGKOK_TZ)
    day_name = DAY_NAMES_TH[local_dt.weekday()]
    month_name = MONTH_NAMES_TH[local_dt.month - 1]
    thai_year = local_dt.year + 543

    return (
        f"\u0e27\u0e31\u0e19{day_name}\u0e17\u0e35\u0e48 {local_dt.day} "
        f"{month_name} {thai_year} {local_dt.hour:02d}:{local_dt.minute:02d}"
    )


def discord_timestamp(dt, style):
    return f"<t:{int(dt.timestamp())}:{style}>"


def iter_versions(start_version, end_version, skip_minor=9):
    start = int(round(start_version * 10))
    end = int(round(end_version * 10))

    for version_num in range(start, end + 1):
        minor = version_num % 10

        if minor == skip_minor:
            continue

        yield f"{version_num // 10}.{minor}"


def build_timeline(start_dates, intervals, start_version, end_version):
    current_dates = dict(start_dates)
    rows = []

    for version in iter_versions(start_version, end_version):
        rows.append((version, dict(current_dates)))

        for phase, interval_days in intervals.items():
            current_dates[phase] += timedelta(days=interval_days)

    return rows


def render_timeline(game_name, rows, phase_labels=None, bullet=False):
    phase_labels = phase_labels or {}
    prefix = " - " if bullet else ""
    lines = []

    for version, dates in rows:
        lines.append(f"{game_name} {version}")

        for phase, dt in dates.items():
            label = phase_labels.get(phase, phase)
            lines.append(
                f"{prefix}Version {version} {label}: "
                f"{discord_timestamp(dt, 'R')} | {discord_timestamp(dt, 'F')} | "
                f"{format_date_th(dt)}"
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_output(markdown_text, output_file):
    output_path = Path(output_file)

    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_text, encoding="utf-8")
    return output_path


def run_timeline(config):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    rows = build_timeline(
        start_dates=config["start_dates"],
        intervals=config["intervals"],
        start_version=config["start_version"],
        end_version=config["end_version"],
    )
    markdown_text = render_timeline(
        game_name=config["game_name"],
        rows=rows,
        phase_labels=config.get("phase_labels"),
        bullet=config.get("bullet", False),
    )

    output_file = config.get("output_file")
    if output_file:
        output_path = write_output(markdown_text, output_file)
        print(f"Saved timeline to {output_path}")
        print()

    print(markdown_text)
