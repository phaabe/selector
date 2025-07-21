#!/usr/bin/env python3

import os
import shutil
import subprocess
import curses

SCROLL_MARGIN = 5

def get_playlist_filenames(target_dir):
    try:
        return set(os.listdir(target_dir))
    except FileNotFoundError:
        return set()

def prompt_create_dir(stdscr, path):
    stdscr.addstr(2, 0, f"Directory '{path}' does not exist. Create it? (y/n): ")
    while True:
        key = stdscr.getch()
        if key in (ord('y'), ord('Y')):
            try:
                os.makedirs(path)
                return True
            except Exception as e:
                stdscr.addstr(3, 0, f"Error creating directory: {e}")
                stdscr.getch()
                return False
        elif key in (ord('n'), ord('N')):
            return False

def filter_entries(entries, filter_text):
    """Return list filtered by all keywords (case-insensitive)."""
    if len(filter_text) < 2:
        return entries
    keywords = filter_text.lower().split()
    filtered = []
    for e in entries:
        e_lower = e.lower()
        if all(k in e_lower for k in keywords):
            filtered.append(e)
    return filtered

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()

    stdscr.addstr(0, 0, "Enter target playlist directory: ")
    curses.echo()
    target_dir = stdscr.getstr().decode().strip()
    curses.noecho()

    if not os.path.exists(target_dir):
        if not prompt_create_dir(stdscr, target_dir):
            return

    if not os.path.isdir(target_dir):
        stdscr.addstr(4, 0, f"Path is not a directory: {target_dir}")
        stdscr.getch()
        return

    start_dir = os.getcwd()
    current_dir = start_dir

    selected_index = 0
    scroll_offset = 0

    filter_mode = False
    filter_text = ""
    filter_active = False

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        max_visible = height - 4  # extra line for filter input display

        try:
            entries = os.listdir(current_dir)
        except PermissionError:
            entries = []

        entries.sort()
        entries = ['..'] + entries

        playlist_files = get_playlist_filenames(target_dir)

        # If filtering active, update filtered_entries accordingly
        if filter_active:
            filtered_entries = filter_entries(entries, filter_text)
        else:
            filtered_entries = entries

        total_items = len(filtered_entries)

        # Adjust scroll offset based on selected_index and margin
        if selected_index < scroll_offset + SCROLL_MARGIN:
            scroll_offset = max(0, selected_index - SCROLL_MARGIN)
        elif selected_index >= scroll_offset + max_visible - SCROLL_MARGIN:
            scroll_offset = min(max(0, total_items - max_visible), selected_index - max_visible + SCROLL_MARGIN + 1)

        # Show current path
        stdscr.addstr(0, 0, f"Current directory: {current_dir[:width-1]}")

        # Show filter input if in filter mode
        if filter_mode:
            stdscr.addstr(1, 0, f"Filter: {filter_text}")
        elif filter_active:
            stdscr.addstr(1, 0, f"Filter active (ESC to clear): {filter_text}")
        else:
            stdscr.addstr(1, 0, "")

        # Display entries (filtered or not)
        for i in range(scroll_offset, min(scroll_offset + max_visible, total_items)):
            entry = filtered_entries[i]
            full_path = os.path.join(current_dir, entry)
            is_file = os.path.isfile(full_path)
            mark = "* " if is_file and entry in playlist_files else "  "
            prefix = "> " if i == selected_index else "  "
            display_line = (prefix + mark + entry)[:width-1]

            try:
                stdscr.addstr(i - scroll_offset + 2, 0, display_line, curses.A_REVERSE if i == selected_index else 0)
            except curses.error:
                pass

        # stdscr.refresh()
        stdscr.noutrefresh()
        curses.doupdate()


        key = stdscr.getch()

        if filter_mode:
            # Handle input in filter mode
            if key in (27,):  # ESC pressed
                filter_mode = False
                filter_active = True if len(filter_text) >= 2 else False
                if not filter_active:
                    filter_text = ""
                # Clamp selected_index if filtered list smaller
                if selected_index >= len(filtered_entries):
                    selected_index = max(0, len(filtered_entries) - 1)
                scroll_offset = 0
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                filter_text = filter_text[:-1]
                filter_active = len(filter_text) >= 2
                selected_index = 0
                scroll_offset = 0
            elif 32 <= key <= 126:  # printable chars
                filter_text += chr(key)
                filter_active = len(filter_text) >= 2
                selected_index = 0
                scroll_offset = 0
            # Ignore other keys while filtering
            continue

        # Not in filter_mode, normal navigation keys:
        if key == ord('j'):
            selected_index = min(total_items - 1, selected_index + 1)
        elif key == ord('k'):
            selected_index = max(0, selected_index - 1)
        elif key in (ord('o'), 10, curses.KEY_ENTER):
            if total_items == 0:
                continue
            selected = filtered_entries[selected_index]
            path = os.path.join(current_dir, selected)
            if os.path.isdir(path):
                current_dir = path
                selected_index = 0
                scroll_offset = 0
                filter_text = ""
                filter_active = False
                filter_mode = False
            elif os.path.isfile(path):
                subprocess.Popen(['xdg-open', path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif key == ord('b'):
            parent = os.path.dirname(current_dir)
            if os.path.commonpath([parent, start_dir]) == start_dir:
                previous_dir_name = os.path.basename(current_dir)
                current_dir = parent

                # Refresh entries and apply filter if active
                try:
                    entries = os.listdir(current_dir)
                except PermissionError:
                    entries = []

                entries.sort()
                entries = ['..'] + entries

                if filter_active:
                    filtered_entries = filter_entries(entries, filter_text)
                else:
                    filtered_entries = entries

                # Try to restore selection to previous folder name
                try:
                    selected_index = filtered_entries.index(previous_dir_name)
                except ValueError:
                    selected_index = 0  # fallback if not found

                scroll_offset = 0
                filter_text = ""
                filter_active = False
                filter_mode = False

        elif key == ord('c'):
            if total_items == 0:
                continue
            selected = filtered_entries[selected_index]
            path = os.path.join(current_dir, selected)
            if os.path.isfile(path):
                try:
                    shutil.copy(path, os.path.join(target_dir, selected))
                except Exception as e:
                    stdscr.addstr(height - 1, 0, f"Error copying: {e}")
                    stdscr.getch()
        elif key == ord('q'):
            break
        elif key == ord('s'):
            # Enter filter mode
            filter_mode = True
            filter_text = ""
            filter_active = False
            selected_index = 0
            scroll_offset = 0
        elif key == 27:  # ESC outside filter mode
            # First ESC disables filter (show all), second ESC has no effect
            if filter_active or filter_mode:
                filter_mode = False
                filter_active = False
                filter_text = ""
                selected_index = 0
                scroll_offset = 0

if __name__ == "__main__":
    curses.wrapper(main)
