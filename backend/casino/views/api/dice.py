def get_wins(dice):
    sorted_dice = sorted(dice)
    wins = []
    total = sum(sorted_dice)

    if 3 < total < 11 and not (sorted_dice[0] == sorted_dice[1] and sorted_dice[1] == sorted_dice[2]):
        wins.append('small')

    if 10 < total < 18 and not (sorted_dice[0] == sorted_dice[1] and sorted_dice[1] == sorted_dice[2]):
        wins.append('big')

    if 3 < total < 18:
        wins.append(f'total-{total}')

    if sorted_dice[0] == sorted_dice[1] and sorted_dice[1] == sorted_dice[2]:
        wins.append(f'triple-{sorted_dice[0]}')
        wins.append('triple-any')

    if sorted_dice[0] == sorted_dice[1] or sorted_dice[0] == sorted_dice[2]:
        wins.append(f'double-{sorted_dice[0]}')

    if sorted_dice[1] == sorted_dice[2]:
        wins.append(f'double-{sorted_dice[1]}')

    if sorted_dice[0] != sorted_dice[1]:
        wins.append(f'pair-{sorted_dice[0]}-{sorted_dice[1]}')

    if sorted_dice[0] != sorted_dice[2]:
        wins.append(f'pair-{sorted_dice[0]}-{sorted_dice[2]}')

    if sorted_dice[1] != sorted_dice[2]:
        wins.append(f'pair-{sorted_dice[1]}-{sorted_dice[2]}')

    wins.append(f'face-{sorted_dice[0]}')
    wins.append(f'face-{sorted_dice[1]}')
    wins.append(f'face-{sorted_dice[2]}')

    return wins
