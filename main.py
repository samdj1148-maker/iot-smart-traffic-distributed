import json

def load_sensors(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def distribute_processing(sensor_data):
    results = {}
    for intersection, sensors in sensor_data.items():
        vehicle_count = sensors['vehicles']
        queue_length = sensors['queue_length']
        green_time = min(120, max(30, queue_length * 2 + vehicle_count // 2))
        results[intersection] = {
            'vehicle_count': vehicle_count,
            'queue_length': queue_length,
            'recommended_green_time': green_time,
            'bottleneck': queue_length > 5 or vehicle_count > 40
        }
    return results

def write_output(results, filename):
    with open(filename, 'w') as f:
        for intersection, res in results.items():
            f.write(f"Intersection {intersection}:\n")
            f.write(f"  Vehicles: {res['vehicle_count']}\n")
            f.write(f"  Queue Length: {res['queue_length']}\n")
            f.write(f"  Recommended Green Time: {res['recommended_green_time']} seconds\n")
            f.write(f"  Bottleneck: {'Yes' if res['bottleneck'] else 'No'}\n\n")
    print("Results written to", filename)

if __name__ == '__main__':
    sensors = load_sensors('input.txt')
    control = distribute_processing(sensors)
    write_output(control, 'output.txt')
