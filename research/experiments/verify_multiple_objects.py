import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


# ============================================================
# SETTINGS
# ============================================================

# Put your multiple-ball image here.
IMAGE_PATH = "images/multi_balls_test.jpg"

# Your existing SAM 2.1 Tiny checkpoint.
CHECKPOINT_PATH = "checkpoints/sam2.1_hiera_tiny.pt"

# Hydra configuration name.
MODEL_CONFIG = "configs/sam2.1/sam2.1_hiera_t.yaml"

# Results will be saved here.
OUTPUT_DIR = Path("outputs/multi_balls")


# ============================================================
# SAVE A BINARY MASK
# ============================================================

def save_binary_mask(mask, path):
    """
    Save the segmentation mask as an image.

    White = selected object
    Black = background
    """

    mask_image = mask.astype(np.uint8) * 255

    cv2.imwrite(
        str(path),
        mask_image
    )


# ============================================================
# FIND BOUNDING BOX
# ============================================================

def get_bounding_box(mask):
    """
    Returns:

    x, y, width, height

    around the selected object.
    """

    ys, xs = np.where(mask)

    if len(xs) == 0 or len(ys) == 0:
        return None

    x_min = int(xs.min())
    x_max = int(xs.max())

    y_min = int(ys.min())
    y_max = int(ys.max())

    width = x_max - x_min + 1
    height = y_max - y_min + 1

    return (
        x_min,
        y_min,
        width,
        height,
    )


# ============================================================
# FIND CENTROID
# ============================================================

def get_centroid(mask):
    """
    Finds the geometric center of the mask.

    This is NOT necessarily the physical center of mass.
    """

    ys, xs = np.where(mask)

    if len(xs) == 0:
        return None

    center_x = float(xs.mean())
    center_y = float(ys.mean())

    return center_x, center_y


# ============================================================
# SAVE TRANSPARENT OBJECT
# ============================================================

def save_transparent_object(
    image_rgb,
    mask,
    full_output_path,
    crop_output_path,
):
    """
    Creates a transparent PNG.

    Object pixels remain visible.
    Background becomes transparent.
    """

    alpha = mask.astype(np.uint8) * 255

    # RGB + Alpha channel
    rgba = np.dstack(
        [
            image_rgb,
            alpha
        ]
    )

    # OpenCV saves in BGRA order.
    bgra = cv2.cvtColor(
        rgba,
        cv2.COLOR_RGBA2BGRA
    )

    # Save full-sized transparent version.
    cv2.imwrite(
        str(full_output_path),
        bgra
    )

    # Find object position.
    bbox = get_bounding_box(mask)

    if bbox is None:
        return None

    x, y, width, height = bbox

    # Crop only the object area.
    cropped = bgra[
        y:y + height,
        x:x + width
    ]

    cv2.imwrite(
        str(crop_output_path),
        cropped
    )

    return bbox


# ============================================================
# DISPLAY ALL SAM CANDIDATES
# ============================================================

def show_candidate_masks(
    image,
    masks,
    scores,
    point_coords,
    object_number,
):
    """
    For each clicked object, SAM normally returns
    multiple possible masks.

    Top row:
        pure black/white mask

    Bottom row:
        mask overlay on original image
    """

    number_of_masks = len(masks)

    fig, axes = plt.subplots(
        2,
        number_of_masks,
        figsize=(5 * number_of_masks, 9)
    )

    # Safety for one-mask case.
    if number_of_masks == 1:
        axes = np.array(
            [
                [axes[0]],
                [axes[1]]
            ]
        )

    for i, mask in enumerate(masks):

        # ----------------------------------------------------
        # TOP: BINARY MASK
        # ----------------------------------------------------

        axes[0, i].imshow(
            mask.astype(np.uint8),
            cmap="gray",
            vmin=0,
            vmax=1
        )

        axes[0, i].scatter(
            point_coords[:, 0],
            point_coords[:, 1],
            marker="*",
            color="red",
            s=180
        )

        axes[0, i].set_title(
            f"Candidate {i}\n"
            f"SAM score = {scores[i]:.4f}"
        )

        axes[0, i].axis("off")

        # ----------------------------------------------------
        # BOTTOM: CORRECT TRANSPARENT OVERLAY
        # ----------------------------------------------------

        axes[1, i].imshow(image)

        overlay = np.zeros(
            (
                image.shape[0],
                image.shape[1],
                4
            ),
            dtype=np.float32
        )

        # ONLY selected mask pixels get color.
        overlay[mask > 0] = [
            0.0,
            1.0,
            0.0,
            0.45
        ]

        axes[1, i].imshow(overlay)

        axes[1, i].scatter(
            point_coords[:, 0],
            point_coords[:, 1],
            marker="*",
            color="red",
            s=180
        )

        axes[1, i].set_title(
            f"Candidate {i} Overlay"
        )

        axes[1, i].axis("off")

    fig.suptitle(
        f"Object {object_number}: "
        f"Check which mask is correct",
        fontsize=16
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# ASK USER WHICH MASK IS CORRECT
# ============================================================

def choose_candidate(number_of_masks):

    while True:

        answer = input(
            f"Choose correct mask "
            f"(0-{number_of_masks - 1}) "
            f"or Q if none are correct: "
        ).strip().lower()

        if answer == "q":
            return None

        try:
            index = int(answer)

            if 0 <= index < number_of_masks:
                return index

        except ValueError:
            pass

        print("Invalid input. Try again.")


# ============================================================
# DISPLAY FINAL VERIFIED OBJECTS
# ============================================================

def show_final_result(
    image,
    selected_objects
):

    plt.figure(
        figsize=(11, 8)
    )

    plt.imshow(image)

    for obj in selected_objects:

        mask = obj["mask"]

        overlay = np.zeros(
            (
                image.shape[0],
                image.shape[1],
                4
            ),
            dtype=np.float32
        )

        overlay[mask] = [
            0.0,
            1.0,
            0.0,
            0.35
        ]

        plt.imshow(overlay)

        x, y = obj["prompt"]

        plt.scatter(
            x,
            y,
            marker="*",
            color="red",
            s=180
        )

        plt.text(
            x + 10,
            y,
            f"Object {obj['id']}",
            fontsize=12
        )

    plt.title(
        "Final Verified Object Masks"
    )

    plt.axis("off")

    plt.show()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    # --------------------------------------------------------
    # STEP 1: SELECT GPU OR CPU
    # --------------------------------------------------------

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print()
    print("=" * 60)
    print("DEVICE")
    print("=" * 60)

    print(
        "Device:",
        device
    )

    if device == "cuda":

        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    # --------------------------------------------------------
    # STEP 2: CREATE OUTPUT FOLDER
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # STEP 3: LOAD SAM 2
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("LOADING SAM 2")
    print("=" * 60)

    sam2_model = build_sam2(
        MODEL_CONFIG,
        CHECKPOINT_PATH,
        device=device
    )

    # Model is being used for prediction only.
    sam2_model.eval()

    predictor = SAM2ImagePredictor(
        sam2_model
    )

    print(
        "SAM 2 loaded successfully!"
    )

    # --------------------------------------------------------
    # STEP 4: LOAD IMAGE
    # --------------------------------------------------------

    image = cv2.imread(
        IMAGE_PATH
    )

    if image is None:

        raise FileNotFoundError(
            f"Could not load {IMAGE_PATH}"
        )

    # OpenCV loads BGR.
    # SAM/Matplotlib use RGB.
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    height, width = image.shape[:2]

    print()
    print("=" * 60)
    print("IMAGE")
    print("=" * 60)

    print(
        "Image:",
        IMAGE_PATH
    )

    print(
        "Image size:",
        width,
        "x",
        height
    )

    # --------------------------------------------------------
    # STEP 5: GIVE IMAGE TO SAM 2
    # --------------------------------------------------------

    print()
    print(
        "Encoding image..."
    )

    with torch.inference_mode():

        predictor.set_image(
            image
        )

    print(
        "Image encoded successfully."
    )

    # --------------------------------------------------------
    # STEP 6: USER CLICKS MULTIPLE OBJECTS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("SELECT OBJECTS")
    print("=" * 60)

    print(
        "A window will open."
    )

    print(
        "LEFT-CLICK once inside each ball/object."
    )

    print(
        "After clicking all objects, press ENTER."
    )

    plt.figure(
        figsize=(11, 8)
    )

    plt.imshow(image)

    plt.title(
        "Click once inside EACH object, "
        "then press Enter"
    )

    plt.axis("off")

    clicked_points = plt.ginput(
        n=-1,
        timeout=0,
        show_clicks=True
    )

    plt.close()

    if len(clicked_points) == 0:

        print(
            "No points selected."
        )

        return

    print()
    print(
        "Number of selected objects:",
        len(clicked_points)
    )

    for i, point in enumerate(
        clicked_points,
        start=1
    ):

        print(
            f"Object {i} point:",
            point
        )

    # --------------------------------------------------------
    # STEP 7: PROCESS EACH CLICK SEPARATELY
    # --------------------------------------------------------

    selected_objects = []

    metadata_objects = []

    for object_number, clicked_point in enumerate(
        clicked_points,
        start=1
    ):

        print()
        print("=" * 60)

        print(
            f"PROCESSING OBJECT {object_number}"
        )

        print("=" * 60)

        x, y = clicked_point

        # One positive point for this object.
        point_coords = np.array(
            [
                [x, y]
            ],
            dtype=np.float32
        )

        # 1 means positive/foreground point.
        point_labels = np.array(
            [1],
            dtype=np.int32
        )

        # ----------------------------------------------------
        # STEP 8: SAM PREDICTION
        # ----------------------------------------------------

        with torch.inference_mode():

            masks, scores, logits = (
                predictor.predict(
                    point_coords=point_coords,
                    point_labels=point_labels,
                    multimask_output=True
                )
            )

        print(
            "Number of masks:",
            len(masks)
        )

        print(
            "Scores:",
            scores
        )

        # ----------------------------------------------------
        # STEP 9: SHOW ALL CANDIDATES
        # ----------------------------------------------------

        show_candidate_masks(
            image=image,
            masks=masks,
            scores=scores,
            point_coords=point_coords,
            object_number=object_number
        )

        # ----------------------------------------------------
        # STEP 10: HUMAN VERIFICATION
        # ----------------------------------------------------

        selected_index = choose_candidate(
            len(masks)
        )

        if selected_index is None:

            print(
                f"Object {object_number}: "
                f"rejected."
            )

            continue

        selected_mask = masks[
            selected_index
        ].astype(bool)

        selected_score = float(
            scores[selected_index]
        )

        print(
            "Accepted candidate:",
            selected_index
        )

        print(
            "SAM predicted mask quality:",
            selected_score
        )

        # ----------------------------------------------------
        # STEP 11: OBJECT OUTPUT DIRECTORY
        # ----------------------------------------------------

        object_dir = (
            OUTPUT_DIR
            / f"object_{object_number:02d}"
        )

        object_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # STEP 12: SAVE THE FINAL MASK
        # ----------------------------------------------------

        mask_path = (
            object_dir
            / "mask.png"
        )

        save_binary_mask(
            selected_mask,
            mask_path
        )

        # ----------------------------------------------------
        # STEP 13: SAVE TRANSPARENT OBJECT
        # ----------------------------------------------------

        full_object_path = (
            object_dir
            / "object_full.png"
        )

        crop_object_path = (
            object_dir
            / "object_crop.png"
        )

        bbox = save_transparent_object(
            image_rgb=image,
            mask=selected_mask,
            full_output_path=full_object_path,
            crop_output_path=crop_object_path
        )

        # ----------------------------------------------------
        # STEP 14: GET CENTROID
        # ----------------------------------------------------

        centroid = get_centroid(
            selected_mask
        )

        # Number of pixels belonging to object.
        mask_area = int(
            selected_mask.sum()
        )

        # ----------------------------------------------------
        # STEP 15: SAVE ALL CANDIDATE MASKS
        # ----------------------------------------------------

        for candidate_index, candidate_mask in enumerate(
            masks
        ):

            candidate_path = (
                object_dir
                / f"candidate_{candidate_index}.png"
            )

            save_binary_mask(
                candidate_mask,
                candidate_path
            )

        # ----------------------------------------------------
        # SAVE INFORMATION FOR FINAL DISPLAY
        # ----------------------------------------------------

        selected_objects.append(
            {
                "id": object_number,

                "mask": selected_mask,

                "prompt": [
                    float(x),
                    float(y)
                ]
            }
        )

        # ----------------------------------------------------
        # SAVE INFORMATION FOR JSON METADATA
        # ----------------------------------------------------

        metadata_objects.append(
            {
                "object_id": object_number,

                "positive_prompt": {
                    "x": float(x),
                    "y": float(y)
                },

                "candidate_scores": [
                    float(score)
                    for score in scores
                ],

                "selected_candidate":
                    int(selected_index),

                "selected_score":
                    selected_score,

                "bounding_box_xywh":
                    list(bbox)
                    if bbox is not None
                    else None,

                "centroid_xy":
                    [
                        float(centroid[0]),
                        float(centroid[1])
                    ]
                    if centroid is not None
                    else None,

                "mask_area_pixels":
                    mask_area,

                "files": {
                    "mask":
                        str(mask_path),

                    "transparent_full":
                        str(full_object_path),

                    "transparent_crop":
                        str(crop_object_path)
                }
            }
        )

    # --------------------------------------------------------
    # STEP 16: DISPLAY ALL ACCEPTED OBJECTS
    # --------------------------------------------------------

    if len(selected_objects) > 0:

        show_final_result(
            image,
            selected_objects
        )

    # --------------------------------------------------------
    # STEP 17: SAVE METADATA.JSON
    # --------------------------------------------------------

    metadata = {

        "image":
            IMAGE_PATH,

        "image_width":
            width,

        "image_height":
            height,

        "model":
            "SAM 2.1 Hiera Tiny",

        "checkpoint":
            CHECKPOINT_PATH,

        "coordinate_system": {
            "origin":
                "top-left",

            "x_direction":
                "right",

            "y_direction":
                "down",

            "units":
                "pixels"
        },

        "number_of_clicked_objects":
            len(clicked_points),

        "number_of_accepted_objects":
            len(metadata_objects),

        "objects":
            metadata_objects
    }

    metadata_path = (
        OUTPUT_DIR
        / "metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FINISHED")
    print("=" * 60)

    print(
        "Accepted objects:",
        len(metadata_objects)
    )

    print(
        "Results saved in:",
        OUTPUT_DIR.resolve()
    )

    print(
        "Metadata saved in:",
        metadata_path.resolve()
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()