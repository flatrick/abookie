# abookie

abookie is an audiobook player for the desktop. It plays single-file and multi-file books (m4b, m4a, mp3, opus, ogg, flac), follows chapters, and remembers where you stopped.

Linux is the first target. The code keeps macOS and Windows possible, but no work goes into them before the Linux MVP.

abookie's own code is released into the public domain under [The Unlicense](LICENSE).

## System dependency: libmpv

Playback uses [libmpv](https://mpv.io/). It is a system library and is not bundled. Install it with your distribution's package manager:

| Distribution  | Command                      |
|---------------|------------------------------|
| Arch Linux    | `sudo pacman -S mpv`         |
| Debian/Ubuntu | `sudo apt install libmpv2`   |
| Fedora        | `sudo dnf install mpv-libs`  |

If libmpv is missing, abookie tells you at startup which library is missing and how to install it.

## Development setup

You need [uv](https://docs.astral.sh/uv/), libmpv (above), and optionally [gir](https://github.com/flatrick/git-it-right) for the git hooks.

```sh
git clone https://github.com/flatrick/abookie.git
cd abookie
uv sync
gir init
uv run pytest
```

`uv sync` creates the virtual environment and installs all dependencies, including the development tools. `gir init` turns on the git hooks in `.githooks/` (commit-message check, auto-formatting on commit, full checks on push).

Run the application with `uv run abookie`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how changes are made and [AGENTS.md](AGENTS.md) for the full command list.
