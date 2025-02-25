import matplotlib.pyplot as plt
import os
import random
from PIL import Image, ExifTags
import numpy as np

# Constants
DEFAULT_ELO = 1000
K_FACTOR = 32
RANKINGS_FILE = "rankings.txt"

# Global state
directory = "images"
image_filenames = []
elo_rankings = {}
current_pair = None


def load_images(directory):
    """Loads all image filenames from the specified directory."""
    return sorted(
        [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    )


def random_pair():
    """Selects a random pair of images."""
    return random.sample(image_filenames, 2) if len(image_filenames) >= 2 else None


def get_rankings(directory, filename=RANKINGS_FILE):
    """Loads or initializes Elo rankings for images in the directory."""
    filenames = set(load_images(directory))
    rankings = {f: DEFAULT_ELO for f in filenames}

    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                name, score = line.strip().split(":")
                if name in filenames:
                    rankings[name] = float(score)

    return rankings if filenames == set(rankings.keys()) else {f: DEFAULT_ELO for f in filenames}


def fix_orientation(image_path):
    """Opens an image, auto-rotates it based on EXIF metadata, and returns it as a NumPy array."""
    image = Image.open(image_path)

    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break

        exif = image._getexif()
        if exif and orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        pass  # No EXIF metadata, ignore rotation

    return np.array(image)  # Convert to NumPy array for Matplotlib


def show_images(pair):
    """Displays the given image pair in the same Matplotlib window, auto-correcting orientation."""
    global fig, axs, current_pair
    current_pair = pair

    for i, img_file in enumerate(pair):
        img_path = os.path.join(directory, img_file)
        img = fix_orientation(img_path)  # Fix rotation

        axs[i].clear()
        axs[i].imshow(img)
        axs[i].axis("off")

    # Use figure-wide title to avoid overlap
    fig.suptitle("Press A (left) | D (right) | R (rankings) | E (exit)", fontsize=12, y=0.95)

    # Add voting instructions below images
    axs[0].set_xlabel("A - Vote Left", fontsize=12, labelpad=10)
    axs[1].set_xlabel("D - Vote Right", fontsize=12, labelpad=10)

    fig.tight_layout()  # Adjust spacing
    fig.canvas.draw()


def next_pair():
    """Displays the next random image pair."""
    pair = random_pair()
    if pair:
        show_images(pair)
    else:
        print("Not enough images to display a pair.")


def elo_update(rankings, winner, loser, k=K_FACTOR):
    """Updates Elo rankings based on the winner/loser."""
    exp_win = 1 / (1 + 10 ** ((rankings[loser] - rankings[winner]) / 400))
    rankings[winner] += k * (1 - exp_win)
    rankings[loser] -= k * exp_win
    return rankings


def update_ranking(winner, loser):
    """Updates rankings and loads the next pair."""
    global elo_rankings
    elo_rankings = elo_update(elo_rankings, winner, loser)
    next_pair()


def save_rankings():
    """Saves Elo rankings to file."""
    sorted_rankings = sorted(elo_rankings.items(), key=lambda x: x[1], reverse=True)
    with open(RANKINGS_FILE, "w") as file:
        for filename, ranking in sorted_rankings:
            file.write(f"{filename}:{ranking}\n")


def show_rankings():
    """Displays the top three ranked images in a separate window with rankings."""
    top_images = sorted(elo_rankings.items(), key=lambda x: x[1], reverse=True)[:3]

    if len(top_images) == 0:
        print("No rankings available.")
        return

    fig_rank, axs_rank = plt.subplots(1, 3, figsize=(12, 5))

    for i, (img_file, score) in enumerate(top_images):
        img_path = os.path.join(directory, img_file)
        img = fix_orientation(img_path)  # Fix rotation

        axs_rank[i].imshow(img)
        axs_rank[i].axis("off")
        axs_rank[i].set_title(f"#{i + 1}: {score:.1f}", fontsize=12)

    fig_rank.suptitle("Top 3 Ranked Images", fontsize=14)
    plt.show()


def on_key(event):
    """Handles keyboard input for voting and opening rankings."""
    if event.key in ["a", "d"]:
        winner, loser = (current_pair[0], current_pair[1]) if event.key == "a" else (current_pair[1], current_pair[0])
        update_ranking(winner, loser)
    elif event.key == "e":
        plt.close(fig)
        save_rankings()
    elif event.key == "r":
        show_rankings()


# Initialize the GUI
image_filenames = load_images(directory)
elo_rankings = get_rankings(directory)

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
fig.canvas.mpl_connect("key_press_event", on_key)

next_pair()
plt.show()
