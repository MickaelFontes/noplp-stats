import contextlib
import csv
import difflib
import io
import subprocess


def compare_diff():
    diff_output = get_git_diff_output()
    lines = diff_output.splitlines()[4:]
    added_lines, removed_lines = parse_diff_lines(lines)
    updated_songs, new_songs, removed_songs = categorize_songs(
        added_lines, removed_lines
    )
    print_song_changes(updated_songs, new_songs, removed_songs)


def get_git_diff_output():
    return subprocess.check_output(
        [
            "git",
            "diff",
            "origin/main:data/db_lyrics.csv",
            "origin/update-noplp-database:data/db_lyrics.csv",
            "-U0",
        ]
    ).decode("utf-8")


def parse_diff_lines(lines):
    added_lines = []
    removed_lines = []
    for line in lines:
        song_details = list(csv.reader([line[1:]]))[0]
        if line.startswith("-"):
            removed_lines.append(song_details)
        elif line.startswith("+"):
            added_lines.append(song_details)
    return added_lines, removed_lines


def categorize_songs(added_lines, removed_lines):
    updated_songs = []
    plus_titles = {line[0] for line in added_lines}
    minus_titles = {line[0] for line in removed_lines}
    updated_titles = plus_titles & minus_titles
    new_songs = [
        song for song in added_lines if song[0] in list(plus_titles - updated_titles)
    ]
    removed_songs = [
        song for song in removed_lines if song[0] in list(minus_titles - updated_titles)
    ]
    for added_line in added_lines:
        if added_line[0] in updated_titles:
            removed_line = next(
                (song for song in removed_lines if song[0] == added_line[0]), None
            )
            if removed_line and removed_line[2] != added_line[2]:
                updated_songs.append(
                    (added_line[0], added_line[1], diff(removed_line[2], added_line[2]))
                )
    return updated_songs, new_songs, removed_songs


def print_song_changes(updated_songs, new_songs, removed_songs):
    is_first_section = True
    if len(updated_songs) > 0:
        print("Updated songs:\n")
        for song in sorted(list(updated_songs), key=lambda x: x[0]):
            parse_song_print(song)
        is_first_section = False
    if len(new_songs) > 0:
        if not is_first_section:
            print("\n----")
        print("New songs:\n")
        for song in sorted(list(new_songs), key=lambda x: x[0]):
            parse_song_print(song, unescape_new_line=True)
        is_first_section = False
    if len(removed_songs) > 0:
        if not is_first_section:
            print("\n----")
        print("Removed songs:\n")
        for song in sorted(list(removed_songs), key=lambda x: x[0]):
            parse_song_print(song, title_only=True)


def parse_song_print(song, unescape_new_line=False, title_only=False):
    if title_only:
        print(f"* {song[0]}, de {song[1]}\n")
        return
    print("<details>")
    print(f"<summary>{song[0]}, de {song[1]}</summary>\n\n<pre><code>")
    if unescape_new_line:
        print(song[2].replace("\\n", "\n"))
    else:
        print(song[2])
    print("</code></pre>\n\n</details>")


def diff(old_lyrics, new_lyrics):
    # Crée un objet StringIO pour capturer la sortie de print()
    old_output = io.StringIO()
    new_output = io.StringIO()

    # Redirige la sortie de print() vers l'objet StringIO
    with contextlib.redirect_stdout(old_output):
        print(old_lyrics)
    with contextlib.redirect_stdout(new_output):
        print(new_lyrics)

    # Récupère la sortie de print() sous forme de chaîne de caractères
    old_output = old_output.getvalue().strip().replace("\\n", "\n")
    new_output = new_output.getvalue().strip().replace("\\n", "\n")

    expected = old_output.splitlines(1)
    actual = new_output.splitlines(1)

    diff_files = "".join(difflib.unified_diff(expected, actual))

    return diff_files


# Call the function
compare_diff()
