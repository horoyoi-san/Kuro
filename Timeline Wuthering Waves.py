from datetime import datetime, timedelta

# วันที่เริ่มต้น 2.5 ตาม timestamp ที่คุณให้
dates_corrected = {
    "Drip": datetime.fromtimestamp(1750219200),    # 18 กรกฎาคม 2025
    "Beta": datetime.fromtimestamp(1750933200),    # 26 กรกฎาคม 2025
    "Release": datetime.fromtimestamp(1753153200)  # 22 สิงหาคม 2025
}

start_version = 2.5
end_version = 8.0

current_dates = dates_corrected.copy()
output = []

version = start_version
while version <= end_version:
    # ข้ามเวอร์ชันที่ลงท้ายด้วย .9
    if round(version * 10) % 10 == 9:
        version = round(version + 0.1, 1)
        continue
    
    version_str = f"{version:.1f}"
    output.append(f"# Wuthering Waves {version_str}")
    output.append(f"Version {version_str} Drip: <t:{int(current_dates['Drip'].timestamp())}:R> | <t:{int(current_dates['Drip'].timestamp())}:F>")
    output.append(f"Version {version_str} Beta: <t:{int(current_dates['Beta'].timestamp())}:R> | <t:{int(current_dates['Beta'].timestamp())}:F>")
    output.append(f"Version {version_str}: <t:{int(current_dates['Release'].timestamp())}:R> | <t:{int(current_dates['Release'].timestamp())}:F>")
    output.append("")  # ว่างบรรทัดเพิ่มความอ่านง่าย
    
    # เพิ่มวันสำหรับเวอร์ชันถัดไป
    current_dates["Drip"] += timedelta(days=42)
    current_dates["Beta"] += timedelta(days=42)
    current_dates["Release"] += timedelta(days=41)
    
    version = round(version + 0.1, 1)

print("\n".join(output))
