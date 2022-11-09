#pylint: disable=invalid-name, line-too-long
LIBRARIES={
    "cmake":{
        "download_opts": ["https://cmake.org/files/v3.15/cmake-3.15.4.tar.gz", "cmake-3.15.4.tar.gz"],
        "folder_name": "cmake-3.15.4"
    },
    "lame":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["https://codeload.github.com/openstreamcaster/lame/zip/master", "lame-master.zip"],
        "folder_name": "lame-master"
    },
    "libopus":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz", "opus-1.3.1.tar.gz"],
        "folder_name": "opus-1.3.1"
    },
    "libogg":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["http://downloads.xiph.org/releases/ogg/libogg-1.3.3.tar.gz", "libogg-1.3.3.tar.gz"],
        "folder_name": "libogg-1.3.3"
    },
    "libtheora":{
        "configure_opts": ["--disable-shared", "--enable-static", "--disable-oggtest", "--disable-vorbistest", "--disable-examples", "--disable-asm", "--disable-spec"],
        "download_opts": ["http://downloads.xiph.org/releases/theora/libtheora-1.1.1.tar.gz", "libtheora-1.1.1.tar.bz"],
        "folder_name": "libtheora-1.1.1"
    },
    "libvpx":{
        "configure_opts": ["--disable-shared", "--disable-unit-tests"],
        "download_opts": ["https://github.com/webmproject/libvpx/archive/v1.8.1.tar.gz", "libvpx-1.8.1.tar.gz"],
        "folder_name": "libvpx-1.8.1"
    },
    "libvorbis":{
        "configure_opts": ["--disable-shared", "--enable-static", "--disable-oggtest"],
        "download_opts": ["http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.6.tar.gz", "libvorbis-1.3.6.tar.gz"],
        "folder_name": "libvorbis-1.3.6"
    },
    "opencore":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["http://downloads.sourceforge.net/project/opencore-amr/opencore-amr/opencore-amr-0.1.5.tar.gz", "opencore-amr-0.1.5.tar.gz"],
        "folder_name": "opencore-amr-0.1.5"
    },
    "pkg-config":{
        "configure_opts": ["--silent", "--with-internal-glib"],
        "download_opts": ["http://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz", "pkg-config-0.29.2.tar.gz"],
        "folder_name": "pkg-config-0.29.2"
    },
    "nasm":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.gz", "nasm.tar.gz"],
        "folder_name": "nasm-2.14.02"
    },
    "x264":{
        "configure_opts": ["--enable-static", "--enable-pic"],
        "download_opts": ["https://code.videolan.org/videolan/x264/-/archive/stable/x264-stable.tar.gz", "x264-stable.tar.gz"],
        "folder_name": "x264-stable"
    },
    "vidstab":{
        "configuration": "cmake",
        "configure_opts": ["-DBUILD_SHARED_LIBS=OFF", "-DUSE_OMP=OFF", "-DENABLE_SHARED=off", "."],
        "download_opts": ["https://github.com/georgmartius/vid.stab/archive/v1.1.0.tar.gz", "georgmartius-vid.stab-v1.1.0-0-g60d65da.tar.gz"],
        "folder_name": "vid.stab-1.1.0"
    },
    "xvidcore":{
        "configure_opts": ["--disable-shared", "--enable-static"],
        "download_opts": ["https://downloads.xvid.com/downloads/xvidcore-1.3.5.tar.gz", "xvidcore-1.3.5.tar.gz"],
        "folder_name": ["xvidcore", "build", "generic"]
    },
    "yasm":{
        "download_opts": ["http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz", "yasm-1.3.0.tar.gz"],
        "folder_name": "yasm-1.3.0"
    }
}

SHELL = 'bash'

# Set up constants
DOWNLOAD_RETRY_DELAY = 3
DOWNLOAD_RETRY_ATTEMPTS = 3

# Pseudographics
BOLD_SEPARATOR = "======================================="
ITALIC_SEPARATOR = "---------------------------------------"

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
    to_print = strings + (ITALIC_SEPARATOR,)
    print_lines(*to_print)


def print_block(*strings):
    to_print = strings + (BOLD_SEPARATOR,)
    print_lines(*to_print)
    print("")


def print_p(*strings):
    to_print = strings
    print_lines(*to_print)
    print("")

# Please note that neat features of Plumbum like FG, BG and TEE are not working on Windows.
# Especially TEE that runs `select` against new processes.
# Therefore, now we have no meaningful debug output whatsoever.
# It's a huge problem, but I know no quick fixes, and Windows is too important now.
# https://github.com/tomerfiliba/plumbum/issues/170
#
# A temporary solution:
# Plumbum provides enough information for a very basic log-driven debugging though.
# For a deep understanding of underlying errors you have to hack this script by yourself to add some reporting.

def fg(command, *args, silent=False):
    try:
        if silent:
            (local[command][args])() #pylint: disable=pointless-statement
        else:
            return True
    except Exception as e: #pylint: disable=broad-except
        print(f"Failed to execute in foreground\n{e}")
        return False

def add_path(dir_name, take_priority=True) -> None:
    """
    Add directory to PATH env

    Returns
    -------
    None
    """
    old_path = local.env["PATH"]
    if take_priority:
        new_path = f"{dir_name}:{old_path}"
    else:
        new_path = f"{old_path}:{dir_name}"
    local.env["PATH"] = new_path

def mkdir(*dir_tree) -> None:
    """
    Create directory

    Retuns
    ------
    None
    """
    dir_name = path_join(*dir_tree)
    if not os.path.exists(dir_name):
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)
        if is_exists(dir_name):
            print(f"Directory {dir_name} created successfully")
            return
        print(f"Directory {dir_name} can't be created")
        return
    print(f"Directory {dir_name} already exists, can't create")

def mkdirs(*dirs) -> None:
    """
    Create multiple directiory

    Returns
    -------
    None
    """
    for current_dir in dirs:
        mkdir(current_dir)


def rmdir(dir_name) -> None:
    """
    Remove directory

    Returns
    -------
    None
    """
    if not os.path.exists(dir_name):
        print(f"Directory {dir_name} doesn't exist, no need to remove it")
        return
    os.rmdir(dir_name)
    if is_exists(dir_name):
        print(f"Directory {dir_name} still exists, can't remove")
        return
    print(f"Directory {dir_name} removed successfully")

def rm(*file_tree) -> None:
    """
    Remove file

    Returns
    -------
    None
    """
    file_name = path_join(*file_tree)
    if not os.path.exists(file_name):
        print(f"File {file_name} doesn't exist, no need to remove it")
        return
    os.remove(file_name)
    if is_exists(file_name):
        print(f"File {file_name} still exists, can't remove")
        return
    print(f"File {file_name} removed successfully")

def command_exists(cmd: str) -> bool:
    """
    Check if commands exist (used at require_commands function)

    Returns
    -------
    bool
    """
    try:
        local[cmd] #pylint: disable=pointless-statement
        return True
    except CommandNotFound:
        return False

def require_commands(*commands) -> None:
    """
    Check if commands exist

    Returns
    -------
    None
    """
    absent_commands_list = [command for command in commands if not command_exists(command)]
    if absent_commands_list:
        absent = ', '.join(absent_commands_list)
        print(f"Required commands not found: {absent}")
        sys.exit(1)

def clean_all(release_dir, target_dir) -> None:
    """
    Clean all build file

    Returns
    -------
    None
    """
    print("Cleaning started")
    rmdir(release_dir)
    rmdir(target_dir)
    print("Cleaning finished")

def make(threads, *args, **kwargs) -> None:
    """
    Make command

    Returns
    -------
    None
    """
    print("Running make...")
    if not fg("make", "-j", threads, *args, **kwargs):
        sys.exit(1)
    print("Make done.")

def install(*args, **kwargs) -> None:
    """
    Make install

    Returns
    -------
    None
    """
    print("Installing...")
    if not fg("make", "install", *args,  **kwargs):
        sys.exit(1)
    print("Installation done.")

class Builder:
    def __init__(self,
            os_type,
            target_dir: str="targets",
            release_dir: str="release",
            bin_dir: str="bin",
        ):
        """"""
        self.__dir_data={
            "target_dir": path_join(CWD, target_dir),
            "release_dir": path_join(CWD, release_dir),
            "bin_dir": path_join(CWD, release_dir, bin_dir),
            "pkg_config_path": path_join(CWD, release_dir, "lib", "pkgconfig")
        }
        self.__ffmpeg_opts = tuple()

        #Value will filled at build function
        self.__event={
                'pre_configure': self.__pre_configure,
                'post_configure': self.__post_configure,
                'post_install': self.__post_install,
            }
        self.__old_ldflags=None
        self.__os_type=os_type
        self.__targets=[]

    @property
    def target_dir(self) -> str:
        """
        Returns
        -------
        str
            Return target dir
        """
        return self.__dir_data['target_dir']

    @property
    def release_dir(self) -> str:
        """
        Returns
        -------
        str
            Returnr release dir
        """
        return self.__dir_data['release_dir']

    @property
    def bin_dir(self) -> str:
        """
        Returns
        -------
        str
            Return binary dir
        """
        return self.__dir_data['bin_dir']

    @property
    def pkg_config_path(self) -> str:
        """
        Returns
        -------
        str
            Return pkg config path
        """
        return self.__dir_data['pkg_config_path']

    @property
    def is_windows(self) -> bool:
        """
        Returns
        -------
        bool
        """
        return self.__os_type == 'Windows'

    @property
    def is_linux(self) -> bool:
        """
        Returns
        -------
        bool
        """
        return self.__os_type == 'Linux'

    @property
    def is_mac(self) -> bool:
        """
        Returns
        -------
        bool
        """
        return self.__os_type == 'Darwin'

    def __pre_configure(self, lib):
        """
        This function will executed before configure
        """
        if lib == 'cmake':
            rm("Modules", "FindJava.cmake")
            (local["perl"][ "-p", "-i", "-e", "s/get_filename_component.JNIPATH/#get_filename_component(JNIPATH/g", "Tests/CMakeLists.txt"])()

        elif lib == "libvpx" and self.is_mac:
            print("Patching libvpx for MacOS")
            ((local["sed"]["s/,--version-script//g", "build/make/Makefile"]) > "build/make/Makefile.patched")()
            ((local["sed"]["s/-Wl,--no-undefined -Wl,-soname/-Wl,-undefined,error -Wl,-install_name/g",
                "build/make/Makefile.patched"]) > "build/make/Makefile")()

        elif lib == 'libopus':
            # On Windows, there's a huge problem.
            # "Unlike glibc, mingw-w64 does not provide fortified functions at all...
            # "... actually it does now, but its broken as hell :S"
            #
            # MinGW: https://github.com/msys2/MINGW-packages/issues/5803
            # Opus: https://github.com/bincrafters/community/issues/1077
            #
            # Solution:
            # Fortification requires -lssp (or -fstack-protector which adds -lssp implicitly) to work.
            self.__old_ldflags = local.env.get("LDFLAGS")
            if self.is_windows:
                if self.__old_ldflags is not None:
                    local.env["LDFLAGS"] = f"{self.__old_ldflags} -fstack-protector"
                else:
                    local.env["LDFLAGS"] = " -fstack-protector"

        elif lib == 'libvorbis':
            LIBRARIES['libvorbis']['configure_opts'].append([
                f"--with-ogg-libraries={self.path_fixer(self.release_dir)}/lib",
                f"--with-ogg-includes={self.path_fixer(self.release_dir)}/include"
            ])

        elif lib == 'libtheora':
            print("Removing --fforce-adr from configure")
            ((local["sed"]["s/-fforce-addr//g", "configure"]) > "configure.patched") & FG #pylint: disable=pointless-statement
            fg("chmod", "+x", "configure.patched")
            fg("mv", "configure.patched", "configure")
            print("Configure processing done.")
            LIBRARIES['libtheora']['configure_opts'].append([
                f"--with-ogg-libraries={self.release_dir}/lib",
                f"--with-ogg-includes={self.release_dir}/include/",
                f"--with-vorbis-libraries={self.release_dir}/lib",
                f"--with-vorbis-includes={self.release_dir}/include/"
            ])

        elif lib == 'pkg-config':
            LIBRARIES['pkg-config']['configure_opts'].append([f"--with-pc-path={self.release_dir}/lib/pkgconfig"])

        elif lib == 'x264':
            if self.is_linux:
                LIBRARIES['x264']['configure_opts'].append(['CXXFLAGS=\"-fPIC\"'])

    def __post_configure(self, lib):
        if lib == "lame":
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
            fg("chmod", "+x", "install-sh")

        elif lib == 'libopus':
            # Restore old LDFLAGS after all that dark magic
            if self.is_windows and self.__old_ldflags is not None:
                local.env["LDFLAGS"] = self.__old_ldflags

    def __post_install(self, lib):
        if lib == 'xvidcore':
            dylib_file = path_join(self.target_dir, "lib", "libxvidcore.4.dylib")
            if is_exists(dylib_file):
                rm(dylib_file)

    def build(self,
            targets: list,
            extra_cflags: Optional[str]=None,
            extra_ldflags: Optional[str]=None,
            threads: Optional[int]=None,
            is_slavery_mode: bool=False,
            silent: bool=False
            ):
        """
        Function to run build
        """
        extra_cflags=f"-I{self.release_dir}/include {extra_cflags}"
        extra_ldflags=f"-L{self.release_dir}/lib {extra_ldflags}"
        self.__targets=targets

        if threads is None:
            from psutil import cpu_count #pylint: disable=import-outside-toplevel
            threads = cpu_count(logical=False)
            if self.is_mac:
                self.__ffmpeg_opts = ("--enable-videotoolbox",)

        print_header("Building process started")
        mkdirs(self.target_dir, self.release_dir)
        add_path(self.bin_dir)
        require_commands("make", "g++", "curl", "tar")

        for library in targets:
            if self.is_needed(library):
                self.download(*LIBRARIES[library]['download_opts'])
                with self.target_cwd(*LIBRARIES[library]['folder_name'] if isinstance(LIBRARIES[library]['folder_name'], list) else LIBRARIES[library]['folder_name']):
                    self.__event['pre_configure'](library)
                    if LIBRARIES[library].get("configuration", "configure") == "cmake":
                        self.cmake(*LIBRARIES[library].get("configure_opts", [], silent=silent))
                    else:
                        self.configure(self.release_dir, *LIBRARIES[library].get("configure_opts", []), f"CFLAGS={extra_cflags}", f"LDFLAGS={extra_ldflags}", silent=silent)
                    self.__event['post_configure'](library)
                    make(threads, silent=silent)
                    install(silent=silent)
                    self.__event['post_install'](library)
                    self.mark_as_built(library)

        if self.is_needed("x265"):
            self.download("https://bitbucket.org/multicoreware/x265/downloads/x265_3.2.1.tar.gz",
                    "x265-3.2.1.tar.gz")
            with self.target_cwd("x265_3.2.1", "source"):
                self.cmake("-DENABLE_SHARED:bool=off", ".")
                make(threads)
                install()
                ((local["sed"][
                    "s/-lx265/-lx265 -lstdc++/g", f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc"]) > f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc.tmp")()
                fg("mv", f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc.tmp", f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc")
                self.mark_as_built("x265")

        if self.is_needed("fdk_aac"):
            self.download("https://sourceforge.net/projects/opencore-amr/files/fdk-aac/fdk-aac-2.0.0.tar.gz/download?use_mirror=gigenet",
                "fdk-aac-2.0.0.tar.gz")
            with self.target_cwd("fdk-aac-2.0.0"):
                self.configure(self.release_dir, "--disable-shared", "--enable-static")
                make(threads)
                install()
                self.mark_as_built("fdk_aac")

        if self.is_needed("av1"):
            self.download(
                    "https://aomedia.googlesource.com/aom/+archive/60a00de69ca79fe5f51dcbf862aaaa8eb50ec344.tar.gz",
                    "av1.tar.gz", "av1")
            mkdir(self.target_dir, "aom_build")
            with self.target_cwd("aom_build"):
                # TODO: Don't forget about different kinds of cmake (msys/cmake and mingw/cmake)
                self.cmake("-DENABLE_TESTS=0", f"{self.target_dir}/av1")
                make(threads)
                install()
                self.mark_as_built("av1")

        if self.is_needed("zlib"):
            self.download("https://www.zlib.net/zlib-1.2.11.tar.gz",
                    "zlib-1.2.11.tar.gz")
            with self.target_cwd("zlib-1.2.11"):
                if self.is_windows:
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

                    with local.env(INCLUDE_PATH=f"{self.release_dir}/include",
                                LIBRARY_PATH=f"{self.release_dir}/lib",
                                BINARY_PATH=f"{self.release_dir}/bin"):
                        make("-f", "./win32/Makefile.gcc")
                        install("-f", "./win32/Makefile.gcc")
                else:
                    self.configure(self.release_dir)
                    make(threads)
                    install()
                self.mark_as_built("zlib")

        if self.is_needed("openssl"):
            self.download("https://www.openssl.org/source/openssl-1.1.1d.tar.gz",
                    "openssl-1.1.1d.tar.gz")
            with self.target_cwd("openssl-1.1.1d"):
                if not fg("bash",
                        "./config",
                        f"--prefix={self.path_fixer(self.release_dir)}",
                        f"--openssldir={self.path_fixer(self.release_dir)}",
                        f"--with-zlib-include={self.path_fixer(self.release_dir)}/include/",
                        f"--with-zlib-lib={self.path_fixer(self.release_dir)}/lib",
                        "no-shared",
                        "zlib"):
                    sys.exit(1)
                make(threads)
                install()
                self.mark_as_built("openssl")

        if self.is_needed("sdl"):
            self.download("https://www.libsdl.org/release/SDL2-2.0.12.tar.gz",
                "SDL2-2.0.12.tar.gz")
            with self.target_cwd("SDL2-2.0.12"):
                self.configure(self.release_dir, "--disable-shared", "--enable-static")
                make(threads)
                install()
                self.mark_as_built("sdl")

        if self.is_needed("ffmpeg"):
            self.download("https://ffmpeg.org/releases/ffmpeg-5.1.2.tar.xz",
                    "ffmpeg-5.1.2.tar.xz")
            with self.target_cwd("ffmpeg-5.1.2"):
                local.env["PKG_CONFIG_PATH"] = f"{self.path_fixer(self.release_dir)}/lib/pkgconfig"
                opts = (self.release_dir,
                        *self.__ffmpeg_opts,
                        # f"--bindirr={self.path_fixer(self.release_dir)}/bin"
                        # f"--libdir={self.path_fixer(self.release_dir)}/lib",
                        f"--pkgconfigdir={self.path_fixer(self.release_dir)}/lib/pkgconfig",
                        "--pkg-config-flags=--static",
                        f"--extra-cflags=-I{self.path_fixer(self.release_dir)}/include",
                        f"--extra-ldflags=-L{self.path_fixer(self.release_dir)}/lib",
                        "--extra-ldflags=-fstack-protector",
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

                if not is_slavery_mode:
                    print("Applying free replacements for non-free components")
                    opts = opts + ("--enable-gnutls",)

                if is_slavery_mode:
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
                if not self.is_windows:
                    opts = opts + ("--extra-libs=-lpthread",)
                    opts = opts + ("--enable-pthreads",)

                self.configure(*opts)
                make(threads)
                install()
                self.mark_as_built("ffmpeg")

        if self.is_needed("ffmpeg-msys2-deps") and self.is_windows:
            self.download("https://codeload.github.com/olegchir/ffmpeg-windows-deps/zip/master",
                    "ffmpeg-windows-deps-master.zip")
            with self.target_cwd("ffmpeg-windows-deps-master"):
                fg("cp", "-f", "./*", f"{self.release_dir}/bin")
                self.mark_as_built("ffmpeg-msys2-deps")

        print_block()
        print_block(f"Finished: {self.path_fixer(self.release_dir)}/bin/ffmpeg",
                    "You can check correctness of this build by running: "
                    f"{self.path_fixer(self.release_dir)}/bin/ffmpeg -version",
                    "Study the protocols list carefully (e.g, look for rtmps): "
                    f"{self.path_fixer(self.release_dir)}/bin/ffmpeg -protocols",
                    "Enable it temporary in the command line by running: "
                    "export PATH={self.path_fixer(self.release_dir)}/bin:$PATH")
        print_block("And finally. Don't trust the build. Anything in the script output may be a lie.",
                    "Always check what you're doing and run test suite.",
                    "If you don't have one, ask for professional help.")

    def configure(self, prefix: str, *opts, **kwargs) -> None:
        """
        Run configure

        Returns
        -------
        None
        """
        configure_options = ("./configure", f"--prefix={self.path_fixer(prefix)}",) + opts
        if self.is_windows:
            configure_options = ("bash",) + configure_options
        fg("chmod", "+x", "./configure")
        print(f"Configure with flags: {configure_options}")
        if not fg(*configure_options, **kwargs):
            sys.exit(1)
        print("Configuring done.")

    def cmake(self, *args, **kwargs):
        """
        Run CMake
        """
        print("Making with CMake...")
        # MSYS2 with MinGW toolchain
        if self.is_windows:
            args = ("-G", "MSYS Makefiles",) + args

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

        if not fg("cmake", f"-DCMAKE_INSTALL_PREFIX:PATH={self.release_dir}", *args, **kwargs):
            sys.exit(1)
        print("Making with CMake done.")

    def download(self, url, dest_name, alternative_dir=None):
        """
        Function to download file
        """
        download_path = self.target_dir

        if alternative_dir is not None:
            download_path = path_join(download_path, alternative_dir)
            mkdir(download_path)

        base_path = path_join(download_path, dest_name)
        if not is_exists(base_path):
            print(f"Used from local cache: {url}")
            return

        print(f"Downloading {url}")
        successful_download = False
        for _ in range(DOWNLOAD_RETRY_ATTEMPTS):
            if fg("curl", "-L", "--silent", "-o", base_path, url) is True:
                successful_download = True
                break
            print(f"Downloading failed: {url}. Retrying in {DOWNLOAD_RETRY_DELAY} seconds")
            time.sleep(DOWNLOAD_RETRY_DELAY)

        if not successful_download:
            print(f"Failed to download multiple times: {url}")
            sys.exit(1)
        print(f"Successfuly downloaded: {url}")

        if ".tar" in dest_name:
            if fg("tar", "-xvf", self.path_fixer(base_path), "-C", self.path_fixer(download_path), silent=True):
                return
            print(f"Failed to extract {dest_name}")
            sys.exit(1)
        elif ".zip" in dest_name:
            with ZipFile(base_path) as myzip:
                myzip.extractall(download_path)
            return
        raise Exception

    def is_needed(self, target) -> bool:
        """
        Check if library need to build or not

        Returns
        -------
        bool
        """
        if target not in self.__targets:
            return False

        print(f"\nBuilding target: {target}\n{ITALIC_SEPARATOR}")
        if is_exists(path_join(self.target_dir, f"{target}.ok")):
            print_block("Cached version found")
            return False
        print("No cache, needs building")
        return True

    def mark_as_built(self, target):
        """
        Mark if the library has been build
        """
        filename = path_join(self.target_dir, f"{target}.ok")
        print_block(f"Creating a lock file: {filename}")
        with open(filename, "w", encoding="utf-8") as f: #pylint: disable=unused-variable
            pass

    def path_fixer(self, src: str) -> str:
        """
        Fix windows path

        Information
        -----------
        The following code is the poor's man implementation of this:
        https://stackoverflow.com/questions/41492504/how-to-get-native-windows-path-inside-msys-python
        It's working, but maybe we should consider to switch to the full version
        """
        if not self.is_windows:
            return src

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

    def target_cwd(self, *dirs):
        """
        Change current working directiory
        """
        for curr_dir in dirs:
            result_dir = path_join(self.target_dir, curr_dir)
        return local.cwd(result_dir)

def main() -> None:
    """
    Program Entry Point

    Returns
    -------
    None
    """
    parser = ArgumentParser(description='Build a special edition of FFMPEG.')
    parser.add_argument('--jobs', metavar='threads', action="store", dest="jobs", type=int, help='Number of parallel jobs', default=None)
    parser.add_argument('--build', action="store_true", dest="build_mode", help='Run build')
    parser.add_argument('--clean', action="store_true", dest="clean_mode", help='Clean solution')
    parser.add_argument('--silent', action="store_true", dest="silent_mode", help='Disable build debug')
    parser.add_argument('--targets', action="store", dest="targets",
                    help='comma-separated targets for building (empty = build all)')
    parser.add_argument('--exclude-targets', action="store", dest="exclude_targets", help='Don\'t build these')
    parser.add_argument('--extra-cflags', dest="extra_cflags", help='Build extra CFLAGS')
    parser.add_argument('--extra-ldflags', dest="extra_ldflags", help='Build extra LDFLAGS')
    parser.add_argument('--target-dir')
    parser.add_argument('--release-dir')
    parser.add_argument('--use-nonfree-libs', dest="slavery_mode", action='store_true', help="Use non-free libraries", default=True)
    parser.add_argument('--use-system-build-essentials', dest="default_tools", action='store_true', help="Use cmake, nasm, yasm, pkg-config that installed on system", default=False)
    args = parser.parse_args()

    targets=['av1', 'cmake', 'fdk_aac', 'ffmpeg', 'ffmpeg-msys2-deps', 'lame', 'libogg',
             'libvorbis', 'libtheora', 'libvpx', 'nasm', 'opencore', 'openssl', 'libopus',
             'pkg-config', 'sdl', 'vidstab', 'x264', 'x265', 'xvidcore', 'yasm', 'zlib'
            ]
    #Check if user specify specific targets
    targets = args.targets.split(",") if args.targets is not None else targets
    #Check if user exclude some targets
    targets = [x for x in targets if x not in args.exclude_targets.split(",") ] if args.exclude_targets is not None else targets
    targets = [x for x in targets if x not in ('cmake', 'pkg-config', 'nasm', 'yasm')] if args.default_tools else targets

    print_block("Hello, slave, how are you?" if args.slavery_mode else "Building FFmpeg, free as in freedom!")
    print_header("Processing targets:")
    print_block(targets)

    os_type='Windows' if hasattr(sys, 'getwindowsversion') else local['uname']()
    if args.build_mode:
        kwargs={}
        if args.jobs is not None:
            kwargs={"threads": args.jobs}
        Builder(os_type, target_dir=args.target_dir, release_dir=args.release_dir).build(
            targets,
            is_slavery_mode=args.slavery_mode,
            silent=args.silent_mode,
            **kwargs
        )

    if args.clean_mode:
        clean_all(args.target_dir, args.release_dir)

    print("OpenStreamCaster's FFmpeg-builder finished its work. And you?\nSee help for more information")

if __name__ == '__main__':
    import re
    import sys
    import time
    import os
    import pathlib
    from zipfile import ZipFile
    from argparse import ArgumentParser
    from os import getcwd as CWD
    from os.path import exists as is_exists, join as path_join
    from typing import Optional

    try:
        from plumbum import local, FG, CommandNotFound
    except ModuleNotFoundError:
        print("Install plumbum module first")
        sys.exit(1)

    main()
