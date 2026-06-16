import os

base_dir = r"D:\ex_work\AirQualityReview_Project\data\csv_b10\101-AHU01"

# Target directories for RM096, RM097, RM098
rooms_info = {
    "10-1-096": {
        "dir": os.path.join(base_dir, "RM096", "Raw Data"),
        "temp_name": "10-1-096_RMT_2026-05-14_09-05-00_1.Csv",
        "hum_name": "10-1-096_RMH_2026-05-14_08-41-00_1.Csv",
        "press_name": "10-1-096_RDP_2026-05-14_08-40-00_1.Csv"
    },
    "10-1-097": {
        "dir": os.path.join(base_dir, "RM097", "Raw Data"),
        "temp_name": "10-1-097_RMT_2026-05-14_09-05-00_1.Csv",
        "hum_name": "10-1-097_RMH_2026-05-14_08-41-00_1.Csv",
        "press_name": "10-1-097_RDP_2026-05-14_08-40-00_1.Csv"
    },
    "10-1-098": {
        "dir": os.path.join(base_dir, "RM098", "Raw Data"),
        "temp_name": "10-1-098_RMT_2026-05-14_09-05-00_1.Csv",
        "hum_name": "10-1-098_RMH_2026-05-14_08-41-00_1.Csv",
        "press_name": "10-1-098_RDP_2026-05-14_08-40-00_1.Csv"
    }
}

for room_id, info in rooms_info.items():
    os.makedirs(info["dir"], exist_ok=True)
    
    # 1. Temperature File
    temp_lines = [
        "StartDate: Last : 1 Day(s)\n",
        "Interval: 5 minutes\n",
        "Report Print Date/Time: 14/05/2026 / 09:05:00\n",
        "Room Temperature\n",
        "DateTime;Data Source;Value;Alias\n"
    ]
    
    # 2. Humidity File
    hum_lines = [
        "StartDate: Last : 1 Day(s)\n",
        "Interval: 5 minutes\n",
        "Report Print Date/Time: 14/05/2026 / 08:41:00\n",
        "Room Humidity\n",
        "DateTime;Data Source;Value;Alias\n"
    ]
    
    # 3. Pressure File
    press_lines = [
        "StartDate: Last : 1 Day(s)\n",
        "Interval: 5 minutes\n",
        "Report Print Date/Time: 14/05/2026 / 08:40:00\n",
        "Room Pressure\n",
        "DateTime;Data Source;Value;Alias\n"
    ]
    
    # Generate 288 records (5-minute interval for 24 hours of 13/05/2026)
    for hour in range(24):
        for minute in range(0, 60, 5):
            time_str = f"{hour:02d}:{minute:02d}:00"
            dt_str = f"13/05/2026 {time_str}"
            
            # --- Room 10-1-096 ---
            if room_id == "10-1-096":
                # Temperature violation (26.5°C from 10:00 to 11:00, otherwise 21.5°C)
                if 10 <= hour < 11:
                    temp = 26.5
                else:
                    temp = 21.5
                
                # Humidity violation (68.0%RH from 14:00 to 15:00, otherwise 50.0%RH)
                if 14 <= hour < 15:
                    hum = 68.0
                else:
                    hum = 50.0
                
                # Pressure (constant 20.0 Pa)
                pres = 20.0
                
            # --- Room 10-1-097 ---
            elif room_id == "10-1-097":
                temp = 21.5
                hum = 50.0
                # Pressure (22.0 Pa for first half, 18.0 Pa for second half)
                if hour < 12:
                    pres = 22.0
                else:
                    pres = 18.0
                    
            # --- Room 10-1-098 ---
            else:
                temp = 21.5
                hum = 50.0
                pres = 30.0
                
            temp_lines.append(f"{dt_str};sensor_t;{temp};\n")
            hum_lines.append(f"{dt_str};sensor_h;{hum};\n")
            press_lines.append(f"{dt_str};sensor_p;{pres};\n")
            
    # Add footer
    temp_lines.append("_____________________________________________________________________________________________\n")
    hum_lines.append("_____________________________________________________________________________________________\n")
    press_lines.append("_____________________________________________________________________________________________\n")
    
    # Write to files
    with open(os.path.join(info["dir"], info["temp_name"]), "w", encoding="utf-8") as f:
        f.writelines(temp_lines)
    with open(os.path.join(info["dir"], info["hum_name"]), "w", encoding="utf-8") as f:
        f.writelines(hum_lines)
    with open(os.path.join(info["dir"], info["press_name"]), "w", encoding="utf-8") as f:
        f.writelines(press_lines)

print("Successfully generated B10 day 2 raw files for May 13, 2026.")
