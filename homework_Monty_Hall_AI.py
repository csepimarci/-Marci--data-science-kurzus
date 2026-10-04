import random


def simulate(trials=1_000_000):
    stay_wins = 0
    switch_wins = 0

    for _ in range(trials):
        doors = [0, 0, 0]
        car = random.randint(0, 2)
        doors[car] = 1

        choice = random.randint(0, 2)
        if doors[choice] == 1:
            stay_wins += 1

        opened = None
        for door in range(3):
            if door != choice and doors[door] == 0:
                opened = door
                break

        switched_choice = next(door for door in range(3) if door not in (choice, opened))
        if doors[switched_choice] == 1:
            switch_wins += 1

    stay_rate = stay_wins / trials
    switch_rate = switch_wins / trials

    result_text = (
        f"Trials: {trials}\n"
        f"Stay wins: {stay_wins} ({stay_rate:.2%})\n"
        f"Switch wins: {switch_wins} ({switch_rate:.2%})\n"
    )

    print(result_text, end="")
    return result_text


if __name__ == "__main__":
    result = simulate()
    with open("results2.txt", "w", encoding="utf-8") as file:
        file.write(result)
