# selector
A mouseless playlist curating tool.

## Features
- vim key bindings
- search
- open external player like VLC

## How to use it?
1. Run 
    ```sh
    ./selector.py
    ```
2. Insert playlist name (=destination folder)
3. Walk through directories (`j`/`k`) and select tracks (`c`)

## Key Maps

|   Key         |  Functionality  |
|:-------------:|:----------------|
| `j`/`k`       | move up/down    |
| `o` / `ENTER` | **o**pen directory / **o**pen track externally |   
| `b`           | go **b**ack to parent dir |   
| `s`           | **s**earch, use `ESC` to navigate the current search, again `ESC` to discard search      |

## More information
- Opening a track externally (`o`) calls [xdg-open](https://linux.die.net/man/1/xdg-open).