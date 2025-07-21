# Selector
A simple mouseless playlist curating tool.

*simple* means: It mostly just copies files to a folder.

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
| `c`           | **c**opy to/remove from playlist    |
| `o` / `ENTER` | **o**pen directory / **o**pen track externally |   
| `b`           | go **b**ack to parent dir |   
| `s`           | **s**earch, use `ESC` to navigate the current search, again `ESC` to discard search      |

## More information
- Opening a track externally (`o`) calls [xdg-open](https://linux.die.net/man/1/xdg-open).

## Ideas
- Skip through tracks using vim key bindings. Unfortunately VLC does not provide that out of the box. Configuring this is hard. Build a play based on libVLC?
- Generate playlist files in M3U8. Why M3U8? UTF-8 and human readable.
- Parameters like target directory should become configurable via env var or arguments
- `gg` jump to beginning, `G` jump to end
