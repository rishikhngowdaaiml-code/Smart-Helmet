import piexif
from PIL import Image

def to_deg(value, loc):
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 60
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)

def change_to_rational(number):
    f = float(number)
    return (int(f * 100000), 100000)

def add_gps_to_image(image_path, lat, lon):
    try:
        lat_deg = to_deg(lat, ["S", "N"])
        lon_deg = to_deg(lon, ["W", "E"])

        exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
        exiv_lon = (change_to_rational(lon_deg[0]), change_to_rational(lon_deg[1]), change_to_rational(lon_deg[2]))

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            piexif.GPSIFD.GPSLatitude: exiv_lat,
            piexif.GPSIFD.GPSLongitudeRef: lon_deg[3],
            piexif.GPSIFD.GPSLongitude: exiv_lon,
        }

        exif_dict = {"0th": {}, "Exif": {}, "GPS": gps_ifd, "1st": {}, "thumbnail": None}
        exif_bytes = piexif.dump(exif_dict)
        
        im = Image.open(image_path)
        im.save(image_path, "jpeg", exif=exif_bytes)
        return True
    except Exception as e:
        print(f"Error adding GPS EXIF: {e}")
        return False
