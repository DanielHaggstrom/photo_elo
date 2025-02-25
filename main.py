import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import random

# Constants
DEFAULT_ELO = 1000
K_FACTOR = 32
RANKINGS_FILE = "rankings.txt"

# Global state
directory = "images"
image_filenames = []
elo_rankings = {}


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


def elo_update(rankings, winner, loser, k=K_FACTOR):
    """Updates Elo ratings based on a match result."""
    exp_win = 1 / (1 + 10 ** ((rankings[loser] - rankings[winner]) / 400))
    rankings[winner] += k * (1 - exp_win)
    rankings[loser] -= k * exp_win
    return rankings


def save_rankings():
    """Saves the current Elo rankings to a file."""
    sorted_rankings = sorted(elo_rankings.items(), key=lambda x: x[1], reverse=True)
    with open(RANKINGS_FILE, "w") as file:
        for filename, ranking in sorted_rankings:
            file.write(f"{filename}:{ranking}\n")


def update_ranking(winner, loser):
    """Updates rankings and displays a new pair of images."""
    global elo_rankings
    elo_rankings = elo_update(elo_rankings, winner, loser)
    next_pair()


def show_images(pair, fig, axs):
    """Displays the given image pair in the same Matplotlib window."""
    for i, img_file in enumerate(pair):
        img = mpimg.imread(os.path.join(directory, img_file))
        axs[i].clear()
        axs[i].imshow(img)
        axs[i].axis("off")

    # Add voting instructions below images
    axs[0].set_title(f"A - {pair[0]}", fontsize=10, loc="center")
    axs[1].set_title(f"D - {pair[1]}", fontsize=10, loc="center")

    # Add general instructions
    fig.suptitle("Press A (left) | D (right) | E (exit) | R (rankings)", fontsize=12)

    # Redraw the canvas
    fig.canvas.draw()


def next_pair():
    """Displays the next random image pair."""
    global current_pair
    pair = random_pair()
    if pair:
        current_pair = pair
        show_images(pair, fig, axs)
    else:
        print("Not enough images to display a pair.")


def show_rankings():
    """Opens a new window displaying the top 3 images and their rankings."""
    global elo_rankings

    sorted_rankings = sorted(elo_rankings.items(), key=lambda x: x[1], reverse=True)
    top_images = sorted_rankings[:3]  # Top 3 ranked images

    if not top_images:
        print("No images ranked yet.")
        return

    # Create new figure with 4 subplots: 1 for text rankings, 3 for top images
    fig_rank, axs_rank = plt.subplots(1, 4, figsize=(15, 6), gridspec_kw={'width_ratios': [1, 2, 2, 2]})

    # Left panel: Show rankings as text
    ranking_text = "\n".join(f"{img}: {score:.1f}" for img, score in sorted_rankings[:10])
    axs_rank[0].text(0.5, 0.5, ranking_text, fontsize=12, ha="center", va="center")
    axs_rank[0].axis("off")
    axs_rank[0].set_title("Top Rankings", fontsize=14)

    # Right panel: Show top 3 images
    for i, (img_file, score) in enumerate(top_images):
        img = mpimg.imread(os.path.join(directory, img_file))
        axs_rank[i + 1].imshow(img)
        axs_rank[i + 1].set_title(f"{i+1}. {img_file} ({score:.1f})", fontsize=12)
        axs_rank[i + 1].axis("off")

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
