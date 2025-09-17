<div align="center">
<pre>
. ██████╗ ██╗   ██╗     ██████╗ ███████╗.
. ██╔══██╗╚██╗ ██╔╝    ██╔═══██╗██╔════╝.
. ██████╔╝ ╚████╔╝     ██║   ██║█████╗  .
. ██╔═══╝   ╚██╔╝      ██║   ██║██╔══╝  .
. ██║        ██║       ╚██████╔╝██║     .
. ╚═╝        ╚═╝        ╚═════╝ ╚═╝     .
.     █████╗  ██████╗███████╗███████╗   .
.    ██╔══██╗██╔════╝██╔════╝██╔════╝   .
.    ███████║██║     █████╗  ███████╗   .
.    ██╔══██║██║     ██╔══╝  ╚════██║   .
.    ██║  ██║╚██████╗███████╗███████║   .
.    ╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝   .
</pre>
</div>

A terminal-based Blackjack game written in Python using [blessed](https://pypi.org/project/blessed/).

## Features

### Game Modes

- **Normal Mode**: Traditional blackjack with money management ($1,000 starting money)
- **Practice Mode**: Unlimited play without losing money, tracks total winnings/losses

### Complete Blackjack Features

- **Hit, Stand, Double Down**: All standard blackjack actions
- **Split Hands**: Split pairs and play multiple hands simultaneously
- **Blackjack Detection**: Automatic detection and proper payouts (2.5x for blackjack)
- **Dealer AI**: Dealer hits on soft 17, follows standard casino rules
- **Ace Handling**: Smart ace value calculation (1 or 11)

## Installation

### Prerequisites

- Python 3.8+
- Terminal with Unicode support

## Game Rules

### Blackjack Basics

- **Goal**: Get your hand value as close to 21 as possible without going over
- **Card Values**:
  - Number cards (2-10): Face value
  - Face cards (J, Q, K): 10 points
  - Aces: 1 or 11 (automatically optimized)

### Winning Conditions

- **Blackjack**: 21 with first two cards (pays 2.5x)
- **Player Win**: Higher value than dealer without busting (pays 2x)
- **Dealer Bust**: Dealer goes over 21, player wins (pays 2x)
- **Push**: Same value as dealer (bet returned)

### Special Actions

- **Double Down**: Double your bet, receive exactly one more card
- **Split**: Split matching cards into two separate hands (requires additional bet)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
