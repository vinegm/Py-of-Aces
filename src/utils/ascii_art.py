def get_card_ascii(
    rank: str,
    suit: str,
    face_down_text: str = None,
    card_width: int = 10,
    card_height: int = 7,
) -> str:
    min_width, min_height = 5, 5
    if card_width < min_width or card_height < min_height:
        raise ValueError(f"Card size must be at least {min_width}x{min_height}")

    inner_width = card_width - 2
    inner_height = card_height - 2
    suit_line_index = inner_height // 2

    rank_left = rank.ljust(2)
    rank_right = rank.rjust(2)

    lines = ["+" + "-" * inner_width + "+"]

    for i in range(inner_height):
        if face_down_text:
            if i == suit_line_index:
                text = face_down_text.center(inner_width)
                lines.append(f"|{text}|")
            else:
                lines.append("|" + " " * inner_width + "|")
            continue

        if i == 0:
            padding = " " * (inner_width - len(rank_left))
            lines.append(f"|{rank_left}{padding}|")
            continue

        if i == suit_line_index:
            left_pad = (inner_width - 1) // 2
            right_pad = inner_width - left_pad - 1
            lines.append(f"|{' ' * left_pad}{suit}{' ' * right_pad}|")
            continue

        if i == inner_height - 1:
            padding = " " * (inner_width - len(rank_right))
            lines.append(f"|{padding}{rank_right}|")
            continue

        lines.append(f"|{" " * inner_width}|")

    lines.append("+" + "-" * inner_width + "+")
    return "\n".join(lines)


def join_cards(*cards: list[str]) -> str:
    """
    cards: list of ASCII card strings
    Returns a string with the cards side by side.
    """
    card_lines = [card.splitlines() for card in cards]
    combined_lines = ["  ".join(lines) for lines in zip(*card_lines)]

    return "\n".join(combined_lines)
