import matplotlib.pyplot as plt
import os
import random
from PIL import Image, ExifTags
import numpy as np

# Constants
DEFAULT_ELO = 1000
K_FACTOR = 32
RANKINGS_FILE = "rankings.txt"
IMAGE_DIR = "images"

def load_images(directory):
    """Loads all image filenames from the specified directory."""
    return sorted(
        [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    )

def get_rankings(directory, filename=RANKINGS_FILE):
    """Loads or initializes Elo rankings for images in the directory."""
    filenames = set(load_images(directory))
    rankings = {f: DEFAULT_ELO for f in filenames}

    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:
                name, score = line.strip().split(":")
                if name in filenames:
                    rankings[name] = float(score)

    return rankings

def fix_orientation(image_path):
    """Opens an image, auto-rotates it based on EXIF metadata, and ensures correct color format."""
    try:
        image = Image.open(image_path)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break

        exif = image._getexif()
        if exif and orientation in exif:
            orientation = exif[orientation]
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)

        return np.array(image.convert("RGB"))  # Ensures correct color representation

    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return np.zeros((100, 100, 3), dtype=np.uint8)  # Placeholder for failed loads

def show_images(pair):
    """Displays the given image pair in Matplotlib, auto-correcting orientation."""
    global current_pair
    current_pair = pair  # Store current pair for event handling

    print(f"Showing images: {pair[0]} vs {pair[1]}")

    for i, img_file in enumerate(pair):
        img_path = os.path.join(IMAGE_DIR, img_file)
        img = fix_orientation(img_path)

        axs[i].clear()
        axs[i].imshow(img)
        axs[i].axis("off")
        axs[i].set_xlabel("A - Left | D - Right", fontsize=12, labelpad=10)

    fig.suptitle("Press A (left) | D (right) | R (rankings) | E (exit)", fontsize=12, y=0.95)
    fig.tight_layout()
    fig.canvas.draw()

def random_pair(image_list):
    """Selects a random pair of images."""
    return random.sample(image_list, 2) if len(image_list) >= 2 else None

def elo_update(rankings, winner, loser, k=K_FACTOR):
    """Updates Elo rankings based on the winner/loser."""
    exp_win = 1 / (1 + 10 ** ((rankings[loser] - rankings[winner]) / 400))
    rankings[winner] += k * (1 - exp_win)
    rankings[loser] -= k * exp_win

def save_rankings(rankings):
    """Saves Elo rankings to file."""
    with open(RANKINGS_FILE, "w", encoding="utf-8") as file:
        for filename, ranking in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
            file.write(f"{filename}:{ranking}\n")

def show_rankings(rankings):
    """Displays the top three ranked images."""
    top_images = sorted(rankings.items(), key=lambda x: x[1], reverse=True)[:3]

    if not top_images:
        print("No rankings available.")
        return

    fig_rank, axs_rank = plt.subplots(1, len(top_images), figsize=(12, 5))

    for i, (img_file, score) in enumerate(top_images):
        img_path = os.path.join(IMAGE_DIR, img_file)
        img = fix_orientation(img_path)

        axs_rank[i].imshow(img)
        axs_rank[i].axis("off")
        axs_rank[i].set_title(f"#{i + 1}: {score:.1f}", fontsize=12)

    fig_rank.suptitle("Top 3 Ranked Images", fontsize=14)
    plt.show()

def update_ranking(winner, loser, rankings, image_list):
    """Updates rankings and continues the loop by showing the next pair."""
    elo_update(rankings, winner, loser)
    next_pair(image_list, rankings)

def next_pair(image_list, rankings):
    """Displays a new image pair. Runs in an implicit infinite loop until the user exits."""
    global current_pair

    pair = random_pair(image_list)
    if pair:
        show_images(pair)
        current_pair = pair  # Store the new pair
    else:
        print("Not enough images to display a pair.")
        current_pair = None  # Prevents accidental input handling when no images exist

def on_key(event):
    """Handles keyboard input for voting and opening rankings."""
    global current_pair
    if not current_pair:
        return

    if event.key == "a":
        update_ranking(current_pair[0], current_pair[1], elo_rankings, image_filenames)
    elif event.key == "d":
        update_ranking(current_pair[1], current_pair[0], elo_rankings, image_filenames)
    elif event.key == "r":
        show_rankings(elo_rankings)
    elif event.key == "e":
        print("Exiting and saving rankings...")
        save_rankings(elo_rankings)
        plt.close(fig)  # Closes the Matplotlib event loop, effectively stopping the program

# Initialization
image_filenames = load_images(IMAGE_DIR)
elo_rankings = get_rankings(IMAGE_DIR)

if len(image_filenames) < 2:
    print("Not enough images to start the ranking system. Exiting.")
else:
    # Create figure and connect event handling
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    fig.canvas.mpl_connect("key_press_event", on_key)

    # Start the infinite loop implicitly through Matplotlib
    next_pair(image_filenames, elo_rankings)
    plt.show()  # This keeps running until "E" is pressed
