# mAInsweeper

## Reward
The reward is the amount of cells opened.
- A perfect game receives a score of 1
- Opening a safe cell will reward 1/(total # of safe cells)
- Opening a cell that has no effect receives a small penalty
- Opening a mine subtracts 1 from the score

## Installaton
```bash
pip install -r requirements.txt
```

## Demo
```bash
python demo.py
```
<img src="https://i.imgur.com/mKe3vwd.gif" alt="drawing" width="300"/>

`env.render()` defaults to displaying a PyGame visualization.
Alternatively, use `env.render('ansi')` to print
the board to the terminal (broken).

The following information returned by `env.step(action)`.

```python
observation, reward, done, info = env.step(action)
```
```python
info
{
    "opened cells": 29,
    "steps": 1,
    "unnecessary steps": 0,
    "game over": False,
    "opened cell": (0, 7),
    "mine locations": array([[0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 1, 1, 0, 0, 0]])
}
```