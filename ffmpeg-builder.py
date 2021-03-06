import re
import sys
import time
import os
import argparse
import pathlib
from zipfile import ZipFile

from plumbum import local, RETCODE, BG, FG, TEE, CommandNotFound


def add_bool_arg(parser, feature, onexplain, name, offexplain, antiname=None, default=False, required=False):
    if antiname is None:
        antiname = "no-" + name
    group = parser.add_mutually_exclusive_group(required=required)
    group.add_argument('--' + name, dest=feature, action='store_true', help=onexplain)
    group.add_argument('--' + antiname, dest=feature, action='store_false', help=offexplain)
    parser.set_defaults(**{feature: default})  # parser.set_defaults(**{name: default})


# Parse args
parser = argparse.ArgumentParser(description='Build a special edition of FFMPEG.')
parser.add_argument('--jobs', metavar='j', action="store", dest="jobs", type=int, help='number of parallel jobs')
parser.add_argument('--build', action="store_true", dest="build_mode", help='build solution')
parser.add_argument('--clean', action="store_true", dest="clean_mode", help='clean solution')
parser.add_argument('--silent', action="store_true", dest="silent_mode", help='removes most spam')
parser.add_argument('--targets', action="store", dest="targets",
                    help='comma-separated targets for building (empty = build all)')
parser.add_argument('--exclude-targets', action="store", dest="exclude_targets", help='don\'t build these')
add_bool_arg(parser, "slavery_mode", "use non-free components", "slavery",
             "use free components", "freedom",
             True, False)

args = parser.parse_args()

# Set up targets
TARGETS_DEFAULT = ["yasm", "nasm", "opencore", "libvpx", "lame", "opus", "xvidcore", "x264", "libogg",
                   "libvorbis", "libtheora", "pkg-config", "cmake", "vid_stab", "x265", "fdk_aac", "av1",
                   "zlib", "openssl", "sdl", "ffmpeg", "ffmpeg-msys2-deps"]
TARGETS = TARGETS_DEFAULT
if args.targets is not None:
    TARGETS = args.targets.split(",")
if args.exclude_targets is not None:
    EXCLUDE_TARGETS = args.exclude_targets.split(",")
    TARGETS = [x for x in TARGETS if x not in EXCLUDE_TARGETS]

# Aliases
fex = os.path.exists
pj = os.path.join

SHELL = 'bash'

# Set up output directories
CWD = local.cwd
TARGET_DIR = pj(CWD, "targets")
RELEASE_DIR = pj(CWD, "release")
RELEASE_BIN_DIR = pj(RELEASE_DIR, "bin")
PKG_CONFIG_PATH = pj(RELEASE_DIR, "lib", "pkgconfig")

# Set up C/C++ compiler
CC = local["clang"]
LDFLAGS = f"-L{RELEASE_DIR}/lib -lm"
CFLAGS = f"-I{RELEASE_DIR}/include"
FFMPEG_CONFIGURE_EXTENDED_OPTIONS = tuple()
JOBS_DEFAULT = 8
JOBS = JOBS_DEFAULT

# Set up operating system
OS_TYPE_LINUX = "Linux"
OS_TYPE_MAC = "Darwin"
OS_TYPE_WINDOWS = "Windows"
# mad skills: https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
OS_TYPE = OS_TYPE_WINDOWS if hasattr(sys, 'getwindowsversion') else local['uname']()

# Set up constants
DOWNLOAD_RETRY_DELAY = 3
DOWNLOAD_RETRY_ATTEMPTS = 3

ARCHIVE_FORMAT_TAR = "TAR"
ARCHIVE_FORMAT_ZIP = "ZIP"

# Pseudographics
bold_separator = "======================================="
italic_separator = "---------------------------------------"


def cross_platform_path(src):
    if OS_TYPE != OS_TYPE_WINDOWS:
        return src

    # The following code is the poor's man implementation of this:
    # https://stackoverflow.com/questions/41492504/how-to-get-native-windows-path-inside-msys-python
    # It's working, but maybe we should consider to switch to the full version

    # Handle Windows (native path)
    path_search = re.search('([a-zA-Z]):/(.*)', src, re.IGNORECASE)
    if path_search:
        drive = path_search.group(1).lower()
        path = path_search.group(2)
        result = f"/{drive}/{path}"
        return result
    # Handle Windows (native path with backward slashes)
    # Actually we can skip this, but it's useful for validation
    path_search = re.search('([a-zA-Z]):\\\(.*)', src, re.IGNORECASE)
    if path_search:
        drive = path_search.group(1).lower()
        path = path_search.group(2).replace('\\', '/')
        result = f"/{drive}/{path}"
        return result
    # Handle Windows (MSYS2, Git Bash, Cygwin, etc)
    simulated_path_search = re.search('/([a-zA-Z])/(.*)', src, re.IGNORECASE)
    if simulated_path_search:
        drive = simulated_path_search.group(1).lower()
        path = simulated_path_search.group(2)
        result = f"/{drive}/{path}"
        return result
    # No sense in continuing without properly parsed path
    raise NotImplementedError


# Clever alias
cpp = cross_platform_path


def lookahead(iterable):
    it = iter(iterable)
    last = next(it)
    for val in it:
        yield last, True
        last = val
    yield last, False


def print_lines(*strings):
    to_print = ""
    for line, has_more in lookahead(strings):
        to_print = to_print + line + (os.linesep if has_more else "")
    print(to_print)


def print_header(*strings):
    to_print = strings + (italic_separator,)
    print_lines(*to_print)


def print_block(*strings):
    to_print = strings + (bold_separator,)
    print_lines(*to_print)
    print("")


def print_p(*strings):
    to_print = strings
    print_lines(*to_print)
    print("")


def fail():
    sys.exit(1)


# Please note that neat features of Plumbum like FG, BG and TEE are not working on Windows.
# Especially TEE that runs `select` against new processes.
# Therefore, now we have no meaningful debug output whatsoever.
# It's a huge problem, but I know no quick fixes, and Windows is too important now.
# https://github.com/tomerfiliba/plumbum/issues/170
#
# A temporary solution:
# Plumbum provides enough information for a very basic log-driven debugging though.
# For a deep understanding of underlying errors you have to hack this script by yourself to add some reporting.

def fg(a, *cmds):
    try:
        if args.silent_mode:
            (local[a][cmds])()
        else:
            local[a][cmds] & FG
        return True
    except Exception as e:
        print(f"Failed to execute in foreground")
        print(e)
        return False


def sfg(a, *cmds):
    try:
        (local[a][cmds])()
        return True
    except Exception as e:
        print(f"Failed to execute in silent foreground")
        print(e)
        return False


def bg(a, *commands):
    try:
        cmd = local[a]
        p = cmd.popen(*commands)
        p.communicate()
        return True
    except:
        print(f"Failed to execute in background")
        return False


def bg_content(a, *cmds):
    result = local[a][cmds] & BG(retcode=None)
    result.wait()
    return result


def ex(run_in_fg, a, *cmds):
    # Needs further investigation on proper cwd: https://github.com/tomerfiliba/plumbum/issues/320
    if run_in_fg:
        fg(a, cmds)
    else:
        bg(a, cmds)


def push_path(dir_name, take_priority=True):
    old_path = local.env["PATH"]
    if take_priority:
        new_path = f"{dir_name}:{old_path}"
    else:
        new_path = f"{old_path}:{dir_name}"
    local.env["PATH"] = new_path


def mkdir(*dir_name_parts):
    dir_name = pj(*dir_name_parts)
    if not os.path.exists(dir_name):
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)
        if not fex(dir_name):
            print(f"Directory {dir_name} can't be created")
        else:
            print(f"Directory {dir_name} created successfully")
    else:
        print(f"Directory {dir_name} already exists, can't create")


def mkdirs(*dirs):
    for curr_dir in dirs:
        mkdir(curr_dir)


def rmdir(dir_name):
    if not os.path.exists(dir_name):
        print(f"Directory {dir_name} doesn't exist, no need to remove it")
    else:
        os.rmdir(dir_name)
        if not fex(dir_name):
            print(f"Directory {dir_name} removed successfully")
        else:
            print(f"Directory {dir_name} still exists, can't remove")


def rm(*file_name_parts):
    file_name = pj(*file_name_parts)
    if not os.path.exists(file_name):
        print(f"File {file_name} doesn't exist, no need to remove it")
    else:
        os.remove(file_name)
        if not fex(file_name):
            print(f"File {file_name} removed successfully")
        else:
            print(f"File {file_name} still exists, can't remove")


def curl(src, dest):
    # It's a miracle, but crul on MSYS2 use plain paths instead of shielding it with cpp(dest).
    # Trying to shield it will raise an error
    return fg("curl", "-L", "--silent", "-o", dest, src)


def untar(src, dest):
    return sfg("tar", "-xvf", cpp(src), "-C", cpp(dest))


def download(url, dest_name, alter_name=None, archive_format=ARCHIVE_FORMAT_TAR):
    download_path = TARGET_DIR

    if alter_name is not None:
        download_path = pj(TARGET_DIR, alter_name)
        mkdir(download_path)

    base_path = pj(download_path, dest_name)
    if not fex(base_path):
        print(f"Downloading {url}")

        successful_download = False
        for x in range(DOWNLOAD_RETRY_ATTEMPTS):
            if curl(url, base_path) is not True:
                print(f"Downloading failed: {url}. Retrying in {DOWNLOAD_RETRY_DELAY} seconds")
                time.sleep(DOWNLOAD_RETRY_DELAY)
            else:
                successful_download = True
                break

        if not successful_download:
            print(f"Failed to download multiple times: {url}")
            fail()
        else:
            print(f"Successfuly downloaded: {url}")
    else:
        print(f"Used from local cache: {url}")

    if archive_format == ARCHIVE_FORMAT_TAR:
        if not untar(base_path, download_path):
            print(f"Failed to extract {dest_name}")
            fail()
    elif archive_format == ARCHIVE_FORMAT_ZIP:
        with ZipFile(base_path) as myzip:
            myzip.extractall(download_path)
    else:
        raise Exception


def build_lock_file_name(target):
    return pj(TARGET_DIR, f"{target}.ok")


def need_building(target):
    if target not in TARGETS:
        return

    print("")
    print(f"Building target: {target}")
    print(italic_separator)
    if fex(build_lock_file_name(target)):
        print_block("Cached version found")
        return False
    else:
        print("No cache, needs building")
        return True


def mark_as_built(target):
    filename = build_lock_file_name(target)
    print_block(f"Creating a lock file: {filename}")
    return local["touch"][filename] & FG


def command_exists(cmd):
    try:
        local[cmd]
    except CommandNotFound:
        return False
    else:
        return True


def require_commands(*cmds):
    absent_commands_list = []
    for cmd in cmds:
        if not command_exists(cmd):
            absent_commands_list.append(cmd)
    if absent_commands_list:
        absent = ', '.join(absent_commands_list)
        print(f"Required commands not found: {absent}")
        fail()


def target_cwd(*dirs):
    result_dir = TARGET_DIR
    for curr_dir in dirs:
        result_dir = pj(result_dir, curr_dir)
    return local.cwd(result_dir)


def clean_all():
    print("Cleaning started")
    rmdir(RELEASE_DIR)
    rmdir(TARGET_DIR)
    print("Cleaning finished")


def set_jobs_num():
    global JOBS
    global FFMPEG_CONFIGURE_EXTENDED_OPTIONS

    if args.jobs is not None:
        JOBS = args.jobs
    elif fex("/proc/cpuinfo"):
        # Linux
        rslt = bg_content("grep", "-c", "processor", "/proc/cpuinfo")
        JOBS = rslt.stdout.rstrip()
    elif OS_TYPE == OS_TYPE_MAC:
        # Mac
        rslt = bg_content("sysctl", "-n", "machdep.cpu.thread_count")
        JOBS = rslt.stdout.rstrip()
        FFMPEG_CONFIGURE_EXTENDED_OPTIONS = ("--enable-videotoolbox",)
    else:
        # TODO: Windows
        JOBS = JOBS_DEFAULT


def configure(prefix, *opts):
    new_opts = ("./configure", f"--prefix={cpp(prefix)}",) + opts
    if OS_TYPE_WINDOWS == OS_TYPE:
        new_opts = ("bash",) + new_opts
    fg("chmod", "+x", "./configure")
    print(f"Configure with flags: {new_opts}")
    if not fg(*new_opts):
        fail()
    print("Configuring done.")


def make(*opts):
    print(f"Making...")
    if not fg("make", "-j", JOBS, *opts):
        fail()
    print(f"Making done.")


def cmake(*opts):
    print(f"Making with CMake...")
    # MSYS2 with MinGW toolchain
    if OS_TYPE_WINDOWS == OS_TYPE:
        opts = ("-G", "MSYS Makefiles",) + opts

    # For POSIX filenames, use 'msys/cmake'.
    # For Windows paths,  mingw64/mingw-w64-x86_64-cmake'
    # Our self-build bundled version of cmake obviously is build with mingw, so we have to use Windows paths here
    # Failing to do so produces incorrect post-installation code in the cmake_install.cmake:
    # ```
    #    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES
    #    "C:/temp/ffmpeg-builder/targets/x265_3.2.1/source/x265.pc")
    # ```
    # Which is triggered by something like this in CMakeLists.txt:
    # ```
    #    configure_file("x265.pc.in" "x265.pc" @ONLY)
    #    install(FILES       "${CMAKE_CURRENT_BINARY_DIR}/x265.pc"
    #    DESTINATION "${LIB_INSTALL_DIR}/pkgconfig")
    # '''
    # Don't forget that you can search on Windows without grep -r, using
    # something like " dir -Recurse | Select-String -pattern 'x265.pc'" in Power Shell to find errors like this.
    #
    # Discussion: https://cmake.org/pipermail/cmake/2018-February/067058.html
    # Conversions between paths:
    # https://stackoverflow.com/questions/41492504/how-to-get-native-windows-path-inside-msys-python
    # TODO: implement command line option to switch between versions of CMake, protect with cpp(RELEASE_DIR)

    if not fg("cmake", f"-DCMAKE_INSTALL_PREFIX:PATH={RELEASE_DIR}", *opts):
        fail()
    print(f"Making with CMake done.")


def install(*opts):
    print("Installing...")
    if not fg("make", "install", *opts):
        fail()
    print("Installation done.")


def build_all():
    print_header("Building process started")
    mkdirs(TARGET_DIR, RELEASE_DIR)
    push_path(RELEASE_BIN_DIR)
    require_commands("make", "g++", "curl", "tar")
    set_jobs_num()

    if need_building("yasm"):
        download("http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz",
                 "yasm-1.3.0.tar.gz")
        with target_cwd("yasm-1.3.0"):
            configure(RELEASE_DIR)
            make()
            install()
            mark_as_built("yasm")

    if need_building("nasm"):
        download("https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.gz",
                 "nasm.tar.gz")
        with target_cwd("nasm-2.14.02"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            mark_as_built("nasm")

    if need_building("opencore"):
        download(
            "http://downloads.sourceforge.net/project/opencore-amr/opencore-amr/opencore-amr-0.1.5.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Fopencore-amr%2Ffiles%2Fopencore-amr%2F&ts=1442256558&use_mirror=netassist",
            "opencore-amr-0.1.5.tar.gz")
        with target_cwd("opencore-amr-0.1.5"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            mark_as_built("opencore")

    if need_building("libvpx"):
        download("https://github.com/webmproject/libvpx/archive/v1.8.1.tar.gz",
                 "libvpx-1.8.1.tar.gz")
        with target_cwd("libvpx-1.8.1"):
            if OS_TYPE == OS_TYPE_MAC:
                print("Patching libvpx for MacOS")
                ((local["sed"]["s/,--version-script//g", "build/make/Makefile"]) > "build/make/Makefile.patched")()
                ((local["sed"]["s/-Wl,--no-undefined -Wl,-soname/-Wl,-undefined,error -Wl,-install_name/g",
                               "build/make/Makefile.patched"]) > "build/make/Makefile")()
            configure(RELEASE_DIR, "--disable-shared", "--disable-unit-tests")
            make()
            install()
            mark_as_built("libvpx")

    if need_building("lame"):
        # First attempt was to use lame-3.100:
        # http://kent.dl.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz
        # But old version 3.100 breaks Windows compatibility when using libiconv
        # since frontend/parse.c now depends on langinfo.h.
        # https://github.com/bincrafters/community/issues/480
        #
        # We have option to use the latest snapshot from SVN:
        # https://sourceforge.net/p/lame/svn/HEAD/tarball
        # https://sourceforge.net/code-snapshots/svn/l/la/lame/svn/lame-svn-r6449-trunk.zip
        # And get the exact version with: https://sourceforge.net/projects/lame/best_release.json
        #
        # But for now I just imported everything into OpenStreamCaster's space on GitHub:
        # https://codeload.github.com/openstreamcaster/lame/zip/master

        download("https://codeload.github.com/openstreamcaster/lame/zip/master",
                 "lame-master.zip", alter_name=None, archive_format=ARCHIVE_FORMAT_ZIP)
        with target_cwd("lame-master"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            fg("chmod", "+x", "install-sh")
            make()
            install()
            mark_as_built("lame")

    if need_building("opus"):
        download("https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz",
                 "opus-1.3.1.tar.gz")
        with target_cwd("opus-1.3.1"):

            # On Windows, there's a huge problem.
            # "Unlike glibc, mingw-w64 does not provide fortified functions at all...
            # "... actually it does now, but its broken as hell :S"
            #
            # MinGW: https://github.com/msys2/MINGW-packages/issues/5803
            # Opus: https://github.com/bincrafters/community/issues/1077
            #
            # Solution:
            # Fortification requires -lssp (or -fstack-protector which adds -lssp implicitly) to work.

            old_ldflags = local.env.get("LDFLAGS")
            if OS_TYPE == OS_TYPE_WINDOWS:
                if old_ldflags is not None:
                    local.env["LDFLAGS"] = f"{old_ldflags} -fstack-protector"
                else:
                    local.env["LDFLAGS"] = " -fstack-protector"

            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()

            # Restore old LDFLAGS after all that dark magic
            if (OS_TYPE == OS_TYPE_WINDOWS) and (old_ldflags is not None):
                local.env["LDFLAGS"] = old_ldflags

            install()
            mark_as_built("opus")

    if need_building("xvidcore"):
        download("https://downloads.xvid.com/downloads/xvidcore-1.3.5.tar.gz",
                 "xvidcore-1.3.5.tar.gz")
        with target_cwd("xvidcore", "build", "generic"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            dylib_file = pj(TARGET_DIR, "lib", "libxvidcore.4.dylib")
            if fex(dylib_file):
                rm(dylib_file)
            mark_as_built("xvidcore")

    if need_building("x264"):
        download("https://code.videolan.org/videolan/x264/-/archive/stable/x264-stable.tar.bz2",
                 "last_x264.tar.bz2")
        with target_cwd("x264-stable"):
            if OS_TYPE == OS_TYPE_LINUX:
                configure(RELEASE_DIR, "--enable-static", "--enable-pic", 'CXXFLAGS=\"-fPIC\"')
            else:
                configure(RELEASE_DIR, "--enable-static", "--enable-pic")
            make()
            install()
            mark_as_built("x264")

    if need_building("libogg"):
        download("http://downloads.xiph.org/releases/ogg/libogg-1.3.3.tar.gz",
                 "libogg-1.3.3.tar.gz")
        with target_cwd("libogg-1.3.3"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            mark_as_built("libogg")

    if need_building("libvorbis"):
        download("http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.6.tar.gz",
                 "libvorbis-1.3.6.tar.gz")
        with target_cwd("libvorbis-1.3.6"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static", "--disable-oggtest",
                      f"--with-ogg-libraries={cpp(RELEASE_DIR)}/lib",
                      f"--with-ogg-includes={cpp(RELEASE_DIR)}/include")
            make()
            install()
            mark_as_built("libvorbis")

    if need_building("libtheora"):
        download("http://downloads.xiph.org/releases/theora/libtheora-1.1.1.tar.gz",
                 "libtheora-1.1.1.tar.bz")
        with target_cwd("libtheora-1.1.1"):
            print("Removing --fforce-adr from configure")
            ((local["sed"]["s/-fforce-addr//g", "configure"]) > "configure.patched") & FG
            fg("chmod", "+x", "configure.patched")
            fg("mv", "configure.patched", "configure")
            print("Configure processing done.")
            # Always make sure, that you run "./configure" instead of "bash ./configure". Multiple weird errors.
            configure(RELEASE_DIR, "--disable-shared", "--enable-static",
                      "--disable-oggtest", "--disable-vorbistest", "--disable-examples", "--disable-asm",
                      "--disable-spec",
                      f"--with-ogg-libraries={RELEASE_DIR}/lib",
                      f"--with-ogg-includes={RELEASE_DIR}/include/",
                      f"--with-vorbis-libraries={RELEASE_DIR}/lib",
                      f"--with-vorbis-includes={RELEASE_DIR}/include/")
            make()
            install()
            mark_as_built("libtheora")

    if need_building("pkg-config"):
        download("http://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz",
                 "pkg-config-0.29.2.tar.gz")
        with target_cwd("pkg-config-0.29.2"):
            configure(RELEASE_DIR, "--silent", "--with-internal-glib",
                      f"--with-pc-path={RELEASE_DIR}/lib/pkgconfig")
            make()
            install()
            mark_as_built("pkg-config")

    if need_building("cmake"):
        download("https://cmake.org/files/v3.15/cmake-3.15.4.tar.gz",
                 "cmake-3.15.4.tar.gz")
        with target_cwd("cmake-3.15.4"):
            rm("Modules", "FindJava.cmake")
            (local["perl"][
                "-p", "-i", "-e", "s/get_filename_component.JNIPATH/#get_filename_component(JNIPATH/g", "Tests/CMakeLists.txt"])()
            configure(RELEASE_DIR)
            make()
            install()
            mark_as_built("cmake")

    if need_building("vid_stab"):
        download("https://github.com/georgmartius/vid.stab/archive/v1.1.0.tar.gz",
                 "georgmartius-vid.stab-v1.1.0-0-g60d65da.tar.tgz")
        with target_cwd("vid.stab-1.1.0"):
            cmake("-DBUILD_SHARED_LIBS=OFF", "-DUSE_OMP=OFF", "-DENABLE_SHARED:bool=off", ".")
            make()
            install()
            mark_as_built("vid_stab")

    if need_building("x265"):
        download("https://bitbucket.org/multicoreware/x265/downloads/x265_3.2.1.tar.gz",
                 "x265-3.2.1.tar.gz")
        with target_cwd("x265_3.2.1", "source"):
            cmake("-DENABLE_SHARED:bool=off", ".")
            make()
            install()
            ((local["sed"][
                "s/-lx265/-lx265 -lstdc++/g", f"{cpp(RELEASE_DIR)}/lib/pkgconfig/x265.pc"]) > f"{cpp(RELEASE_DIR)}/lib/pkgconfig/x265.pc.tmp")()
            fg("mv", f"{cpp(RELEASE_DIR)}/lib/pkgconfig/x265.pc.tmp", f"{cpp(RELEASE_DIR)}/lib/pkgconfig/x265.pc")
            mark_as_built("x265")

    if need_building("fdk_aac"):
        download(
            "https://sourceforge.net/projects/opencore-amr/files/fdk-aac/fdk-aac-2.0.0.tar.gz/download?use_mirror=gigenet",
            "fdk-aac-2.0.0.tar.gz")
        with target_cwd("fdk-aac-2.0.0"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            mark_as_built("fdk_aac")

    if need_building("av1"):
        download("https://aomedia.googlesource.com/aom/+archive/60a00de69ca79fe5f51dcbf862aaaa8eb50ec344.tar.gz",
                 "av1.tar.gz", "av1")
        mkdir(TARGET_DIR, "aom_build")
        with target_cwd("aom_build"):
            # TODO: Don't forget about different kinds of cmake (msys/cmake and mingw/cmake)
            cmake("-DENABLE_TESTS=0", f"{TARGET_DIR}/av1")
            make()
            install()
            mark_as_built("av1")

    if need_building("zlib"):
        download("https://www.zlib.net/zlib-1.2.11.tar.gz",
                 "zlib-1.2.11.tar.gz")
        with target_cwd("zlib-1.2.11"):
            if OS_TYPE == OS_TYPE_WINDOWS:
                # Problem 1:
                # Please note that
                # Checking for gcc...
                # Please use win32/Makefile.gcc instead.
                # ** ./configure aborting.
                #
                # Problem 2:
                # Making done.
                # Installing...
                # INCLUDE_PATH, LIBRARY_PATH, and BINARY_PATH must be specified
                # make: *** [win32/Makefile.gcc:128: install] Error 1

                with local.env(INCLUDE_PATH=f"{RELEASE_DIR}/include",
                               LIBRARY_PATH=f"{RELEASE_DIR}/lib",
                               BINARY_PATH=f"{RELEASE_DIR}/bin"):
                    make("-f", f"./win32/Makefile.gcc")
                    install("-f", f"./win32/Makefile.gcc")
            else:
                configure(RELEASE_DIR)
                make()
                install()
            mark_as_built("zlib")

    if need_building("openssl"):
        download("https://www.openssl.org/source/openssl-1.1.1d.tar.gz",
                 "openssl-1.1.1d.tar.gz")
        with target_cwd("openssl-1.1.1d"):
            if not fg("bash",
                      "./config",
                      f"--prefix={cpp(RELEASE_DIR)}",
                      f"--openssldir={cpp(RELEASE_DIR)}",
                      f"--with-zlib-include={cpp(RELEASE_DIR)}/include/",
                      f"--with-zlib-lib={cpp(RELEASE_DIR)}/lib",
                      "no-shared",
                      "zlib"):
                fail()
            make()
            install()
            mark_as_built("openssl")

    if need_building("sdl"):
        download(
            "https://www.libsdl.org/release/SDL2-2.0.12.tar.gz",
            "SDL2-2.0.12.tar.gz")
        with target_cwd("SDL2-2.0.12"):
            configure(RELEASE_DIR, "--disable-shared", "--enable-static")
            make()
            install()
            mark_as_built("sdl")

    if need_building("ffmpeg"):
        download("https://git.ffmpeg.org/gitweb/ffmpeg.git/snapshot/8e30502abe62f741cfef1e7b75048ae86a99a50f.tar.gz",
                 "ffmpeg-snapshot.tar.bz2")
        with target_cwd("ffmpeg-8e30502"):
            local.env["PKG_CONFIG_PATH"] = f"{cpp(RELEASE_DIR)}/lib/pkgconfig"
            opts = (RELEASE_DIR,
                    *FFMPEG_CONFIGURE_EXTENDED_OPTIONS,
                    # f"--bindirr={cpp(RELEASE_DIR)}/bin"
                    # f"--libdir={cpp(RELEASE_DIR)}/lib",
                    f"--pkgconfigdir={cpp(RELEASE_DIR)}/lib/pkgconfig",
                    "--pkg-config-flags=--static",
                    f"--extra-cflags=-I{cpp(RELEASE_DIR)}/include",
                    f"--extra-ldflags=-L{cpp(RELEASE_DIR)}/lib",
                    f"--extra-ldflags=-fstack-protector",
                    "--extra-libs=-lm",
                    "--enable-static",
                    "--disable-debug",
                    "--disable-shared",
                    "--enable-ffplay",
                    "--disable-doc",
                    "--enable-gpl",
                    "--enable-version3",
                    "--enable-libvpx",
                    "--enable-libmp3lame",
                    "--enable-libopus",
                    "--enable-libtheora",
                    "--enable-libvorbis",
                    "--enable-libx264",
                    "--enable-libx265",
                    "--enable-runtime-cpudetect",
                    "--enable-avfilter",
                    "--enable-libopencore_amrwb",
                    "--enable-libopencore_amrnb",
                    "--enable-filters",
                    "--enable-libvidstab",
                    "--enable-libaom")

            if not args.slavery_mode:
                print("Applying free replacements for non-free components")
                opts = opts + ("--enable-gnutls",)

            if args.slavery_mode:
                print_p("You are applying dirty non-free attachments. Are you sure you need this?",
                        "Now you can't distribute this FFmpeg build to anyone, so it's almost useless in real products.",
                        "You can't sell or give away these files. Consider using --slavery=false")
                opts = opts + (
                    "--enable-nonfree",
                    # Non-free unfortunately
                    # Should be replaced with gnutls
                    # http://www.iiwnz.com/compile-ffmpeg-with-rtmps-for-facebook/
                    "--enable-openssl",
                    # libfdk_aac is incompatible with the gpl and --enable-nonfree is not specified.
                    # https://trac.ffmpeg.org/wiki/Encode/AAC
                    "--enable-libfdk-aac",)

            # Unfortunately even creators of MSYS2 can't build it with --enable-pthreads :(
            # https://github.com/msys2/MINGW-packages/blob/master/mingw-w64-ffmpeg/PKGBUILD
            if OS_TYPE != OS_TYPE_WINDOWS:
                opts = opts + ("--extra-libs=-lpthread",)
                opts = opts + ("--enable-pthreads",)

            configure(*opts)
            make()
            install()
            mark_as_built("ffmpeg")

    if need_building("ffmpeg-msys2-deps") and (OS_TYPE == OS_TYPE_WINDOWS):
        download("https://codeload.github.com/olegchir/ffmpeg-windows-deps/zip/master",
                 "ffmpeg-windows-deps-master.zip", alter_name=None, archive_format=ARCHIVE_FORMAT_ZIP)
        with target_cwd("ffmpeg-windows-deps-master"):
            fg("cp", "-f", "./*", f"{RELEASE_DIR}/bin")
            mark_as_built("ffmpeg-msys2-deps")

    print_block()
    print_block(f"Finished: {cpp(RELEASE_DIR)}/bin/ffmpeg",
                f"You can check correctness of this build by running: "
                f"{cpp(RELEASE_DIR)}/bin/ffmpeg -version",
                f"Study the protocols list carefully (e.g, look for rtmps): "
                f"{cpp(RELEASE_DIR)}/bin/ffmpeg -protocols",
                f"Enable it temporary in the command line by running: "
                f"export PATH={cpp(RELEASE_DIR)}/bin:$PATH")
    print_block("And finally. Don't trust the build. Anything in the script output may be a lie.",
                "Always check what you're doing and run test suite.",
                "If you don't have one, ask for professional help.")


def main():
    if args.slavery_mode:
        print_block("Hello, slave, how are you?")
    else:
        print_block("Building FFmpeg, free as in freedom!")

    print_header("Processing targets:")
    print_block(f"{TARGETS}")

    if args.clean_mode:
        clean_all()

    if args.build_mode:
        build_all()

    print("OpenStreamCaster's FFmpeg-builder finished its work. And you?")


main()
