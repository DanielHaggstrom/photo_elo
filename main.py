import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import random


def load_images(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]


def random_pair(image_filenames):
    return random.sample(image_filenames, 2) if len(image_filenames) >= 2 else None


def get_rankings(directory, filename="rankings.txt"):
    filenames = set(load_images(directory))
    rankings = {f: 1000 for f in filenames}
    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                name, score = line.strip().split(":")
                if name in filenames:
                    rankings[name] = float(score)
    return rankings if filenames == set(rankings.keys()) else {f: 1000 for f in filenames}


def show_images(pair, directory, fig=None):
    if fig:
        plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    for i, img_file in enumerate(pair):
        img = mpimg.imread(os.path.join(directory, img_file))
        axs[i].imshow(img)
        axs[i].axis('off')

    def on_key(event):
        nonlocal fig
        if event.key in ['a', 'd']:
            update_ranking(pair[0 if event.key == 'a' else 1],
                        pair[1 if event.key == 'a' else 0], fig)
        elif event.key == 'e':
            plt.close(fig)
            save_rankings()

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()


def elo_update(rankings, winner, loser, k=32):
    exp_win = 1 / (1 + 10 ** ((rankings[loser] - rankings[winner]) / 400))
    rankings[winner] += k * (1 - exp_win)
    rankings[loser] -= k * exp_win
    return rankings


def update_ranking(winner, loser, fig):
    global elo_rankings
    elo_rankings = elo_update(elo_rankings, winner, loser)
    next_pair(fig)


def next_pair(fig=None):
    pair = random_pair(image_filenames)
    if pair:
        show_images(pair, directory, fig)


def save_rankings():
    sorted_rankings = sorted(elo_rankings.items(), key=lambda x: x[1], reverse=True)
    with open("rankings.txt", "w") as file:
        for filename, ranking in sorted_rankings:
            print(f"{filename}: {ranking}")
            file.write(f"{filename}:{ranking}\n")


# Example usage
directory = "images"
image_filenames = load_images(directory)
elo_rankings = get_rankings(directory)
next_pair()

