from datetime import datetime, timedelta

# กำหนดวันเริ่มต้น Beta และ Release (ตัวอย่าง)
start_dates = {
    "Drip": datetime(2025, 11, 26, 11, 0),     # 2568 พุธ 11:00
    "Beta CN": datetime(2025, 11, 27, 17, 0),  # 2568 พฤหัสบดี 17:00
    "Beta OS": datetime(2025, 12, 4, 17, 0),   # 2568 พฤหัสบดี 17:00
    "Release": datetime(2025, 12, 25, 10, 0)   # 2568 พฤหัสบดี 10:00
}

start_version = 3.0
end_version = 8.0

# ระยะห่างวัน
drip_interval_days = 42
beta_interval_days = 42
release_interval_days = 42


def format_date_th(dt):
    days_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                 "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    day_name = days_th[dt.weekday()]
    return f"วัน{day_name}ที่ {dt.day} {months_th[dt.month-1]} {dt.year+543} {dt.hour:02d}:{dt.minute:02d}"


# เก็บผลลัพธ์
version_dates = {}

# เริ่มต้นวันที่
current_drip = start_dates["Drip"]
current_beta_cn = start_dates["Beta CN"]
current_beta_os = start_dates["Beta OS"]
current_release = start_dates["Release"]

version = start_version
while version <= end_version:
    if round(version * 10) % 10 != 9:  # ข้าม .9
        key = f"{version:.1f}"
        version_dates[key] = {
            "Drip": current_drip,
            "Beta CN": current_beta_cn,
            "Beta OS": current_beta_os,
            "Release": current_release
        }
        # เลื่อนไปเวอร์ชันถัดไป
        current_drip += timedelta(days=drip_interval_days)
        current_beta_cn += timedelta(days=beta_interval_days)
        current_beta_os += timedelta(days=beta_interval_days)
        current_release += timedelta(days=release_interval_days)
    version = round(version + 0.1, 1)

# แปลงเป็นข้อความ Markdown
markdown_lines = []
for ver, dates in version_dates.items():
    drip_str = format_date_th(dates["Drip"])
    beta_cn_str = format_date_th(dates["Beta CN"])
    beta_os_str = format_date_th(dates["Beta OS"])
    release_str = format_date_th(dates["Release"])

    drip_ts = int(dates["Drip"].timestamp())
    beta_cn_ts = int(dates["Beta CN"].timestamp())
    beta_os_ts = int(dates["Beta OS"].timestamp())
    release_ts = int(dates["Release"].timestamp())

    markdown_lines.append(f"Wuthering Waves {ver}")
    markdown_lines.append(f" - Version {ver} Drip: <t:{drip_ts}:R> | <t:{drip_ts}:F> | {drip_str}")
    markdown_lines.append(f" - Version {ver} Beta CN: <t:{beta_cn_ts}:R> | <t:{beta_cn_ts}:F> | {beta_cn_str}")
    markdown_lines.append(f" - Version {ver} Beta OS: <t:{beta_os_ts}:R> | <t:{beta_os_ts}:F> | {beta_os_str}")
    markdown_lines.append(f" - Version {ver} Release: <t:{release_ts}:R> | <t:{release_ts}:F> | {release_str}")
    markdown_lines.append("")

markdown_text = "\n".join(markdown_lines)
print(markdown_text)
