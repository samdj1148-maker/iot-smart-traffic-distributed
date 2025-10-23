import json
from pathlib import Path

# Simple simulation of distributed smart traffic control using IoT sensor data
# Reads input.txt (JSON) with intersections and sensor readings, computes signal timings, writes output.txt


def compute_cycle(intersection_id, sensors):
    # sensors: dict with approach -> vehicle_count, emergency, pedestrian_wait
    base_green = 20  # seconds
    max_green = 90
    min_green = 10

    allocations = {}
    notes = []

    # Priority to emergency, then queue length, then pedestrian
    for approach, data in sensors.items():
        veh = max(0, int(data.get("vehicle_count", 0)))
        emerg = bool(data.get("emergency", False))
        ped = int(data.get("pedestrian_wait", 0))

        score = veh + (50 if ped > 0 else 0) + (1000 if emerg else 0)
        allocations[approach] = {
            "vehicles": veh,
            "ped_waiting": ped,
            "emergency": emerg,
            "priority_score": score,
        }
        if emerg:
            notes.append(f"{intersection_id}:{approach} emergency priority")

    # Normalize timings proportional to score (ensure at least min_green)
    total_score = sum(max(1, a["priority_score"]) for a in allocations.values())
    cycle_time = 120  # seconds per cycle

    for approach, a in allocations.items():
        share = max(1, a["priority_score"]) / total_score
        green = int(min(max_green, max(min_green, round(share * cycle_time))))
        a["green_seconds"] = green

    # Amber and all-red fixed
    amber = 3
    all_red = 1

    return {
        "intersection": intersection_id,
        "cycle_seconds": cycle_time,
        "amber_seconds": amber,
        "all_red_seconds": all_red,
        "plans": allocations,
        "notes": notes,
    }


def main():
    in_path = Path("input.txt")
    out_path = Path("output.txt")

    if not in_path.exists():
        raise FileNotFoundError("input.txt not found")

    data = json.loads(in_path.read_text())

    results = {
        "policy": "distributed_priority_v1",
        "intersections": [],
    }

    for inter_id, sensors in data.get("intersections", {}).items():
        results["intersections"].append(compute_cycle(inter_id, sensors))

    # Simple coordination: align max priority approaches start times
    max_scores = {}
    for inter in results["intersections"]:
        max_appr = max(inter["plans"].items(), key=lambda kv: kv[1]["priority_score"])[0]
        max_scores[inter["intersection"]] = max_appr
    results["coordination"] = {
        "primary_approaches": max_scores,
        "note": "Align start-of-green for listed approaches across intersections",
    }

    out_path.write_text(json.dumps(results, indent=2))
    print("Wrote output.txt with computed signal plans")


if __name__ == "__main__":
    main()
