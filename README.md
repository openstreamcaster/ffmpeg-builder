# OpenStreamCaster's FFmpeg Builder

Build FFmpeg from scratch with Python!

We already have a bunch of scripts like this. This work is inspired by [ffmpeg-build-script](https://github.com/markus-perl/ffmpeg-build-script/blob/master/build-ffmpeg): Markus did a great job on gathering requirements for multiple components. But I can't use it because of Bash. Bash is a real shit: fragile syntax, no debug, no IDE, no error reporting, nothing. Therefore, it's time to build something similar with a real programming language.

## Usage

* Build:`python3 hello.py --build` and follow on-screen instructions
* Clean:`python3 hello.py --clean`
* Help:`python3 hello.py --help`

## Patches

- TODO: Facebook livestreaming

## Requirements

- GNU/Linux
- MacOS
- TODO: Windows (MSYS2)

## Platforms

- Python 3 (tested on Python 3.8.2, a default version on Ubuntu 20.04)
- TODO: Docker image
- TODO: Ansible Plugin

## License

Universal Permissive License, as in LICENSE.md in this repository.

> The UPL is a lax, non-copyleft license that is compatible with the GNU GPL. The UPL contains provisions dealing explicitly with the grant of patent licenses, whereas many other simple lax licenses only have an implicit grant. 
© [Free Software Foundation](https://www.fsf.org/blogs/licensing/universal-permissive-license-added-to-license-list)

Short hint: you may use it in your Apache 2 or GPL projects, but there's a lot of nuances and implications, so please ask professional help if you don't understand anything about licensing.
