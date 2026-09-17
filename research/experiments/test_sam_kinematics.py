import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Device:", device)

    if device == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))

    # Normal filesystem path
    checkpoint = "checkpoints/sam2.1_hiera_tiny.pt"

    # Hydra config name — NOT a Windows filesystem path
    model_cfg = "configs/sam2.1/sam2.1_hiera_t.yaml"

    print("Loading SAM 2...")

    sam2_model = build_sam2(
        model_cfg,
        checkpoint,
        device=device,
    )

    print("SAM 2 loaded successfully!")

    predictor = SAM2ImagePredictor(sam2_model)

    image = cv2.imread("images/test.jpg")

    if image is None:
        raise FileNotFoundError(
            "Could not load images/test.jpg"
        )

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("Image shape:", image.shape)

    predictor.set_image(image)

    point_coords = np.array(
        [[300, 200]],
        dtype=np.float32
    )

    point_labels = np.array(
        [1],
        dtype=np.int32
    )

    print("Running prediction...")

    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=True,
    )

    print("Number of masks:", len(masks))
    print("Scores:", scores)

    best_mask = masks[np.argmax(scores)]

    plt.figure(figsize=(10, 8))
    plt.imshow(image)
    plt.imshow(best_mask, alpha=0.5)

    plt.scatter(
        point_coords[:, 0],
        point_coords[:, 1],
        marker="*",
        color="red",
        s=200,
    )

    plt.axis("off")
    plt.title("SAM 2 Segmentation")
    plt.show()


if __name__ == "__main__":
    main()