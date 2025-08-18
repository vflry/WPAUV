import csv
import re
import os
import plotly.graph_objects as go
import plotly.io as pio

# Avoid Plotly template compatibility issues
pio.templates.default = "none"

offset_voltage = 2.5 #V

def clean_file(input_file, output_file):
    """
    Clean the binary file by removing non-ASCII bytes (keeps CR/LF/TAB).
    """
    with open(input_file, "rb") as f_in:
        content = f_in.read()
    cleaned = re.sub(rb"[^\x09\x0A\x0D\x20-\x7E]+", b"", content)
    with open(output_file, "wb") as f_out:
        f_out.write(cleaned)
    print(f"✅ Clean file created: {output_file}")


def read_csv_data(csv_file, dist_min=0, dist_max=4000, restart_margin_ms=100, max_delta_ms=1000):
    """
    Read the cleaned CSV and build continuous time series.
    Filters out lines with malformed time, voltage, or distance.
    Handles restarts and time offsets.
    Returns: time, distance, va0, va1, deltav
    """
    time_list, dist_list, va0_list, va1_list, va2_list, dv_list = [], [], [], [], [], []

    header_tokens = ("Time_ms", "Distance_mm", "VA0_V", "VA1_V", "VA2_V")

    time_offset = 0.0
    last_time = None

    with open(csv_file, newline="", encoding="latin1") as f:
        reader = csv.reader(f)

        for line_num, row in enumerate(reader, start=1):
            if not row or all(not c.strip() for c in row):
                continue

            row_joined = " ".join(row)

            # Header
            if all(tok in row_joined for tok in header_tokens):
                print(f"↩️ Restart detected at line {line_num} (header)")
                if last_time is not None:
                    time_offset += last_time
                last_time = 0.0
                continue

            # Try extracting 5 float numbers
            if any(c.strip() == "" for c in row):  # Empty value between commas
                continue
            nums = re.findall(r"[-+]?\d+(?:\.\d+)?", row_joined)
            if len(nums) != 5:
                if any(tok in row_joined for tok in header_tokens):
                    print(f"↩️ Restart detected in line {line_num}")
                    if last_time is not None:
                        time_offset += last_time
                    last_time = 0.0
                    continue
                print(f"⚠️ Skipped line {line_num}: expected 5 numbers, found {len(nums)}")
                continue  # Not the right amount of data

            try:
                t = float(nums[0])
                d = float(nums[1])
                va0 = float(nums[2])
                va1 = float(nums[3])
                va2 = float(nums[4])
                dv = va0 - va1

                # Skip corrupted data
                if t < 0 or t > 1e6:
                    raise ValueError(f"Time out of bounds: {t}")
                if not (dist_min <= d <= dist_max):
                    raise ValueError(f"Distance out of range: {d}")
                if not (-0.5 <= va0 <= 5.5) or not (-0.5 <= va1 <= 5.5) or not (-0.5 <= va2 <= 5.5):
                    raise ValueError(f"Voltage out of plausible range: {va0}, {va1}")

                # Detect restart / time jump
                if last_time is not None:
                    delta = t - last_time
                    if delta < -restart_margin_ms:
                        time_offset += last_time
                        print(f"↩️ Restart detected (rollback) at line {line_num}: t={t} < last={last_time} → offset={time_offset}")
                    elif delta > max_delta_ms:
                        print(f"⚠️ Large time jump at line {line_num}: Δt={delta} ms — skipped")
                        continue

                t_adj = t + time_offset

                time_list.append(t_adj)
                dist_list.append(d)
                va0_list.append(va0)
                va1_list.append(va1)
                va2_list.append(va2-offset_voltage)
                dv_list.append(dv)

                last_time = t

            except Exception as e:
                continue

    return time_list, dist_list, va0_list, va1_list, va2_list, dv_list



def plot_data(time_data, distance_data, va0_data, va1_data, va2_data, deltav_data):
    """
    Plot VA0, VA1, ΔV on primary y-axis (V) and Distance on secondary y-axis (mm).
    """
    if not time_data:
        print("⚠️ No valid data to plot.")
        return

    fig = go.Figure()

    # Voltages
    fig.add_trace(go.Scattergl(x=time_data, y=va0_data, mode="lines", name="VA0 (V)"))
    fig.add_trace(go.Scattergl(x=time_data, y=va1_data, mode="lines", name="VA1 (V)"))
    fig.add_trace(go.Scattergl(x=time_data, y=va2_data, mode="lines", name="V_DC (V)"))
    fig.add_trace(go.Scattergl(x=time_data, y=deltav_data, mode="lines", name="V_AC (V)"))

    # Distance
    fig.add_trace(go.Scattergl(
        x=time_data, y=distance_data, mode="lines", name="Distance (mm)", yaxis="y2"
    ))

    fig.update_layout(
        title="Coil endpoints potentials (A0/A1), DeltaV and VL53L1X distance",
        xaxis=dict(title="Time (ms)"),
        yaxis=dict(title="Voltage (V)"),
        yaxis2=dict(title="Distance (mm)", overlaying="y", side="right"),
        showlegend=True
    )

    fig.show()


if __name__ == "__main__":
    # file path
    raw_file = "<logs/MESURES2.CSV"
    cleaned_file = "mesures_clean.csv"

    clean_file(raw_file, cleaned_file)

    t, d, va0, va1, va2, dv = read_csv_data(cleaned_file)

    plot_data(t, d, va0, va1, va2, dv)