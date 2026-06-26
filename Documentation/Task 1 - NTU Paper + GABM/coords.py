import argparse
from pathlib import Path

import cv2
import pandas as pd

points = []
image_display = None
scale = 1.0
window_name = "Select 4 Points"


def draw_points():
    """Redraw the image with selected points and labels."""
    global image_display
    image_display = display_base.copy()

    for idx, (x_orig, y_orig) in enumerate(points, start=1):
        x_disp = int(round(x_orig * scale))
        y_disp = int(round(y_orig * scale))
        cv2.circle(image_display, (x_disp, y_disp), 6, (0, 0, 255), -1)
        cv2.putText(
            image_display,
            f"P{idx}",
            (x_disp + 10, y_disp - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

    cv2.imshow(window_name, image_display)


def mouse_callback(event, x, y, flags, param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if len(points) >= param["n_points"]:
        print(f"Already selected {param['n_points']} points. Press 'r' to reset or ESC to close.")
        return

    x_orig = int(round(x / scale))
    y_orig = int(round(y / scale))
    points.append((x_orig, y_orig))
    print(f"P{len(points)}: x_px={x_orig}, y_px={y_orig}")
    draw_points()

    if len(points) == param["n_points"]:
        print("\nSelected points complete. Press ESC to save and close, or 'r' to reset.")


def save_points(out_path):
    rows = []
    for idx, (x, y) in enumerate(points, start=1):
        rows.append({
            "point_id": f"P{idx}",
            "x_px": x,
            "y_px": y,
            "x_m": None,
            "y_m": None,
            "notes": "selected using coords.py; fill x_m/y_m manually",
        })

    df = pd.DataFrame(rows, columns=["point_id", "x_px", "y_px", "x_m", "y_m", "notes"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print("\nSelected points:")
    for row in rows:
        print(f"{row['point_id']}: ({row['x_px']}, {row['y_px']})")

    print("\nNotebook-ready point_table snippet:")
    print("point_table = pd.DataFrame([")
    for row in rows:
        print(f"    [\"{row['point_id']}\", {row['x_px']}, {row['y_px']}, np.nan, np.nan, \"{row['notes']}\"],")
    print("], columns=POINT_COLUMNS)")

    print(f"\nSaved CSV: {out_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Click image points and save pixel coordinates for homography.")
    parser.add_argument("image", help="Path to the image/frame, e.g. data/shibuya/frames/reference_candidates/frame.jpg")
    parser.add_argument("--out", default=None, help="Output CSV path. Defaults to data/shibuya/homography_points/selected_image_points.csv")
    parser.add_argument("--n", type=int, default=4, help="Number of points to select. Default: 4")
    parser.add_argument("--max-width", type=int, default=1400, help="Resize display window if image is wider than this. Coordinates are saved in original image pixels.")
    return parser.parse_args()


args = parse_args()
image_path = Path(args.image)
if not image_path.exists():
    raise FileNotFoundError(image_path)

image = cv2.imread(str(image_path))
if image is None:
    raise ValueError(f"Could not load image: {image_path}")

height, width = image.shape[:2]
scale = min(1.0, args.max_width / width) if args.max_width else 1.0
if scale < 1.0:
    display_base = cv2.resize(image, (int(width * scale), int(height * scale)))
else:
    display_base = image.copy()

if args.out is None:
    out_path = Path("data") / "shibuya" / "homography_points" / "selected_image_points.csv"
else:
    out_path = Path(args.out)

print("Image:", image_path)
print("Original size:", width, "x", height)
print("Display scale:", scale)
print(f"Click {args.n} road-plane points in order P1..P{args.n}.")
print("Controls: left click = add point, r = reset, ESC = save and close.")

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setMouseCallback(window_name, mouse_callback, {"n_points": args.n})
draw_points()

while True:
    key = cv2.waitKey(20) & 0xFF
    if key == 27:  # ESC
        break
    if key == ord("r"):
        points.clear()
        print("Reset selected points.")
        draw_points()

cv2.destroyAllWindows()

if points:
    save_points(out_path)
else:
    print("No points selected. Nothing saved.")
