import serial
import time

def convert_to_degrees(raw_value):
    """Convert raw GPS coordinates (ddmm.mmmm) to decimal degrees."""
    degrees = int(raw_value / 100)
    minutes = raw_value - (degrees * 100)
    return degrees + (minutes / 60)

def parse_nmea(sentence):
    """Extracts latitude, longitude, speed, and time from a GPRMC sentence."""
    parts = sentence.split(',')

    if len(parts) < 8 or parts[2] != 'A':  # Check if data is valid ('A' means active)
        return None, None, None, None

    try:
        raw_lat = float(parts[3])  # Latitude in ddmm.mmmm
        lat_dir = parts[4]         # 'N' or 'S'
        raw_lon = float(parts[5])  # Longitude in dddmm.mmmm
        lon_dir = parts[6]         # 'E' or 'W'
        speed_knots = float(parts[7])  # Speed in knots
        utc_time = parts[1]  # UTC time in hhmmss.sss format

        # Convert to decimal degrees
        latitude = convert_to_degrees(raw_lat)
        longitude = convert_to_degrees(raw_lon)

        # Adjust for direction
        if lat_dir == 'S':
            latitude = -latitude
        if lon_dir == 'W':
            longitude = -longitude

        # Convert speed from knots to km/h
        speed_kmh = speed_knots * 1.852  

        return latitude, longitude, speed_kmh, utc_time
    except ValueError:
        return None, None, None, None

try:
    # Open Serial Port
    ser = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
except serial.SerialException as e:
    print(f"Error: Could not open serial port - {e}")
    exit(1)

print("Waiting for GPS data...")

try:
    while True:
        try:
            data = ser.readline().decode("utf-8", errors='ignore').strip()

            if data.startswith("$GPRMC"):  # Look for RMC sentence
                lat, lon, speed, time_utc = parse_nmea(data)

                if lat is not None and lon is not None:
                    print(f"Latitude: {lat:.6f}, Longitude: {lon:.6f}, Speed: {speed:.2f} km/h, Time (UTC): {time_utc}")
                else:
                    print("GPS data not valid.")
        
        except serial.SerialException as e:
            print(f"Serial error: {e}. Retrying...")
            time.sleep(1)  # Wait before retrying
        except UnicodeDecodeError as e:
            print(f"Decode error: {e}. Skipping corrupt data.")

except KeyboardInterrupt:
    print("\nStopping GPS reading.")
finally:
    ser.close()
    print("Serial connection closed.")