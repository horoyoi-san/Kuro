# ================================
# Wuthering Waves Gacha Simulator
# Fixed Version Jump (.9 → next)
# ================================

start_version = (1, 0)   # 2.6
end_version = (3, 0)     # 5.0

pattern = [
    2, -1, 2, -1, 2, 2, -1,
    2, -1, 1, -1, 1, -1, 1, 3, -1, 1, -1,
    "reset"
]


def generate_versions(start, end):
    versions = []
    major, minor = start

    while (major, minor) <= end:
        # ข้าม .9
        if minor == 9:
            major += 1
            minor = 0
            continue

        versions.append(f"{major}.{minor}")

        minor += 1
        if minor > 9:
            major += 1
            minor = 0

    return versions


def simulate_gacha(versions, pattern):
    results = []
    pattern_index = 0
    pull_index = 1

    for version in versions:
        for phase in [1, 2]:

            step = pattern[pattern_index]

            if step == "reset":
                pattern_index = 0
                step = pattern[pattern_index]

            if step == 2:
                result = "ได้ (2)"
            elif step == 1:
                result = "ได้ (1)"
            elif step == -1:
                result = "หลุด (1)"
            else:
                result = "ไม่ทราบ"

            results.append({
                "pull": pull_index,
                "version": version,
                "phase": phase,
                "result": result
            })

            pull_index += 1
            pattern_index += 1

    return results


# ---------- RUN ----------
versions = generate_versions(start_version, end_version)
results = simulate_gacha(versions, pattern)

print("\n===== Wuthering Waves Gacha Simulator =====\n")
for r in results:
    print(
        f"Pull {r['pull']:>2} | "
        f"Version {r['version']} | "
        f"Phase {r['phase']} | "
        f"{r['result']}"
    )
