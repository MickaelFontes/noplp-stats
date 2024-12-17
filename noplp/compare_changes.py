import contextlib
import csv
import difflib
import io
import subprocess


def compare_diff():
    # Get the output of git diff
    diff_output = subprocess.check_output(
        [
            "git",
            "diff",
            "origin/update-noplp-database:data/db_lyrics.csv",
            "origin/main:data/db_lyrics.csv",
            "-U0",
        ]
    ).decode("utf-8")

    # Initialize lines
    lines = diff_output.splitlines()[4:]

    # Initialize variables to store the added and removed lines
    added_lines = []
    removed_lines = []
    updated_songs = []

    # Loop through the lines
    for line in lines:
        song_details = list(csv.reader([line[1:]]))[0]
        # Check if the line is a modification (starting with "-" or "+")
        if line.startswith("-"):
            removed_lines.append(song_details)
        elif line.startswith("+"):
            added_lines.append(song_details)

    # Initialize variables to store the updated, new and removed songs
    plus_titles = {line[0] for line in added_lines}
    minus_titles = {line[0] for line in removed_lines}
    updated_titles = plus_titles & minus_titles
    new_songs = [
        song for song in added_lines if song[0] in list(plus_titles - updated_titles)
    ]
    removed_songs = [
        song for song in removed_lines if song[0] in list(minus_titles - updated_titles)
    ]

    # # Loop through the updated lines
    for added_line in added_lines:
        if added_line[0] in updated_titles:
            # Find associated remove line
            removed_line = next(
                (song for song in removed_lines if song[0] == added_line[0]), None
            )
            # Add the song to the updated songs list
            updated_songs.append(
                (added_line[0], added_line[1], diff(added_line[2], removed_line[2]))
            )

    # Print the results
    print("Updates songs:\n")
    for song in sorted(list(updated_songs), key=lambda x: x[0]):
        parse_song_print(song)
    print("\n----\nNew songs:\n")
    for song in sorted(list(new_songs), key=lambda x: x[0]):
        parse_song_print(song, unescape_new_line=True)
    print("\n----\nRemoved songs:\n")
    for song in sorted(list(removed_songs), key=lambda x: x[0]):
        parse_song_print(song, unescape_new_line=True)


def parse_song_print(song, unescape_new_line=False):
    print("<details>")
    print(f"<summary>{song[0]}, de {song[1]}</summary>\n<pre><code>")
    if unescape_new_line:
        print(song[2].replace("\\n", "\n"))
    else:
        print(song[2])
    print("</code></pre>\n</details>")


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
    # To avoid markdown interpretation fo single hyphen in comment by GitHub
    diff_files = diff_files.replace("\n-\n", "\n\\-\n")

    return diff_files


# Call the function
compare_diff()
