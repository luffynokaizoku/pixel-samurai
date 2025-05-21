# 🔥 TEAM 7 - Samurai Duel Saga

Welcome to **Samurai Duel Saga**, an electrifying 2D pixel art fighting game developed in Python using Pygame! This README provides an in-depth overview of the project, features, architecture, and the minds behind the creation.

---

## 🌟 Game Overview

**Samurai Duel Saga** is a retro-themed action-platformer that brings back the arcade magic of pixel duels. Two legendary samurai engage in fast-paced, tactical battles using swords, special attacks, and platforming maneuvers. The game supports both local Player vs Player (PvP) and Player vs Computer (PvC) modes.

> "Master the art of combat, unleash powerful strikes, and dominate the battlefield in a pixel-perfect showdown!"

---

## 🔹 Core Features

* ✨ **High-Quality Pixel Art**: Custom animations for idle, attack, run, jump, hurt, and death sequences.
* 🎮 **Multiple Game Modes**:

  * **PvP**: Local multiplayer action.
  * **PvC**: Battle against an adaptive AI with varying difficulty levels.
* ⚔️ **Combat Mechanics**:

  * Projectile-based attacks
  * Special power attacks
  * Hit combos and effects
* 🌌 **Platform Dynamics**:

  * Ice (slippery), lava (damaging), and stone terrain.
* 🚀 **Power-Ups**:

  * Health regen
  * Temporary shields
  * Speed boosts
  * Special meter fills
* 🎵 **Sound and Music**:

  * Dynamic sound effects for attacks, jumps, landings, etc.
  * Background soundtrack
* 🛍️ **Menus and UI**:

  * Main menu
  * Options
  * Difficulty settings
  * In-game HUD

---

## 📁 Project Directory Structure

```
samurai-duel-game/
├── assets/
│   ├── backgrounds/
│   │   └── background.png
│   ├── effects/
│   │   └── explosion0.png ... explosion4.png
│   ├── icon/
│   ├── images/
│   ├── player1/
│   │   ├── attack/
│   │   ├── hurt/
│   │   ├── idle/
│   │   ├── jump/
│   │   └── run/
│   ├── player2/
│   │   ├── attack/
│   │   ├── hurt/
│   │   ├── idle/
│   │   ├── jump/
│   │   └── run/
│   ├── sounds/
│   │   └── *.mp3 / *.wav (sound effects)
│   └── ui/
│       └── *.png (sound toggle icons)
├── main.py
├── mh.py
```

---

## 🔧 Installation & Running the Game

### 1. Requirements

* Python 3.8+
* Pygame

### 2. Install Dependencies

```bash
pip install pygame
```

### 3. Launch the Game

```bash
python mh.py
```

### 4. Command Line Options

| Argument       | Description                     | Example                   |
| -------------- | ------------------------------- | ------------------------- |
| `--sound`      | Enable sound                    | `python mh.py --sound`    |
| `--no-sound`   | Disable sound                   | `python mh.py --no-sound` |
| `--difficulty` | AI difficulty: easy/medium/hard | `--difficulty hard`       |
| `--mode`       | Game mode: pvp/pvc              | `--mode pvp`              |

---

## 🤏 Controls

### Player 1

* Move Left: A
* Move Right: D
* Jump: W
* Attack: Spacebar
* Special: S

### Player 2

* Move Left: ←
* Move Right: →
* Jump: ↑
* Attack: Enter
* Special: ↓

---

## 📊 Game Mechanics

### Power-Ups

* **Health**: +20 HP
* **Shield**: Blocks 1 full attack
* **Speed**: Temporarily boosts speed
* **Special**: Fully charges special meter

### AI Difficulty

* **Easy**: Slow response, low aggression
* **Medium**: Balanced gameplay
* **Hard**: Fast, strategic, and brutal

---

## 🏆 Project Team - TEAM 7 🔥

| Name                        | Roll Number |
| --------------------------- | ----------- |
| Sure. Sri Venkat Rama Surya | 231FA04442  |
| Sirigiri. Anand Prabhu Das  | 231FA04436  |
| Reddy. Bala Raju            | 231FA04432  |

---

## 🙏 Acknowledgments

* Developed using **Pygame**
* Pixel art and sounds sourced from open/free licensed repositories
* Special thanks to our mentors and peers for testing and feedback

---

## 🚀 Future Improvements

* Online multiplayer mode (using sockets)
* More characters with unique abilities
* Dynamic weather effects in stages
* Save/load player statistics

---

## 💡 License

This project is for educational use and not intended for commercial distribution.

---

## 🚀 Ready to Fight?

Run `python mh.py` and unleash your inner samurai!

> "In the pixel dojo of destiny, the blade speaks louder than words..."
