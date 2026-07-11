from pathlib import Path
import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="VisDrone YOLOv8n test inference")
    parser.add_argument("source", help="Path to image or folder")
    parser.add_argument(
        "--weights",
        default="runs/detect/runs/detect/visdrone_yolov8n/weights/best.pt",
        help="Path to best.pt",
    )
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--out", default="runs/predict", help="Output project dir")
    args = parser.parse_args()

    weights = Path(args.weights)
    if not weights.exists():
        raise FileNotFoundError(
            f"Weights not found: {weights}\n"
        )
    model = YOLO(str(weights))
    model.predict(
        source=args.source,
        conf=args.conf,
        save=True,
        project=args.out,
        name="visdrone",
        exist_ok=True,
    )
    print("Done. Check:", Path(args.out) / "visdrone")


if __name__ == "__main__":
    main()