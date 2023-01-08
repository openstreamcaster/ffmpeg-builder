#pylint: disable=invalid-name, line-too-long, missing-module-docstring
from typing import Optional, Iterable, Union
# Set up constants
DOWNLOAD_RETRY_DELAY = 3
DOWNLOAD_RETRY_ATTEMPTS = 3

# Pseudographics
BOLD_SEPARATOR = "======================================="
ITALIC_SEPARATOR = "---------------------------------------"

def findText(filePath: str, text: str) -> Union[None, int]:
    """
    Find text in file

    Parameters
    ----------
    filePath: str
        File path in string
    text: str
        Text that you wanna find

    Returns
    -------
    Return either None or int
    """
    with open(filePath) as file:
        for index, value in enumerate(file.readlines()):
            if text == value.strip():
                file.close()
                return index

def delete_lines(filePath: str, start: int, end: int) -> None:
    """
    Function to delete lines in the file from specific
    start and specific end

    Parameters
    ----------
    filePath: str
        File path in string
    start: int
        Start line
    end: int
        Stop line

    Returns
    -------
    None
    """
    with open(filePath) as fRead:
        file_read=fRead.readlines()
        fRead.close()
    with open(filePath, "w") as fWrite:
        for index, value in enumerate(file_read):
            if index < start or index > end:
                fWrite.write(value)
        fWrite.close()

def lookahead(iterable: Iterable):
    """
    Lookahead function

    Parameters
    ----------
    iterable: Iterable
        Iterable value

    Returns
    -------
    None
    """
    it=iter(iterable)
    for value in it:
        try:
            yield value, next(it)
        except StopIteration:
            yield value, False

def print_lines(*strings) -> None:
    """
    Print strings line by line

    Parameters
    ----------
    *strings
        List of string

    Returns
    -------
    None
    """
    to_print = ""
    for line, has_more in lookahead(strings):
        to_print = to_print + line + ("\n" if has_more else "")
    print(to_print)

def print_header(*strings) -> None:
    """
    Print strings with italic separator and line by line

    Parameters
    ----------
    *strings
        List of string

    Returns
    -------
    None
    """
    to_print = strings + (ITALIC_SEPARATOR,)
    print_lines(*to_print)

def print_block(*strings) -> None:
    """
    Print strings with bold separator and line by line

    Parameters
    ----------
    *strings
        List of string

    Returns
    -------
    None
    """
    to_print = strings + (BOLD_SEPARATOR,)
    print_lines(*to_print)
    print()

# Please note that neat features of Plumbum like FG, BG and TEE are not working on Windows.
# Especially TEE that runs `select` against new processes.
# Therefore, now we have no meaningful debug output whatsoever.
# It's a huge problem, but I know no quick fixes, and Windows is too important now.
# https://github.com/tomerfiliba/plumbum/issues/170
#
# A temporary solution:
# Plumbum provides enough information for a very basic log-driven debugging though.
# For a deep understanding of underlying errors you have to hack this script by yourself to add some reporting.

def fg(command: str, *args, silent: bool=False) -> bool:
    """
    Run command at foreground

    Parameters
    ----------
    command: str
        Command
    *args
        Command additional argument
    silent: bool
        Print foreground result or not

    Returns
    -------
    bool
    """
    try:
        if silent:
            (local[command][args])() #pylint: disable=pointless-statement
        else:
            local[command][args] & FG #pylint: disable=pointless-statement
        return True
    except Exception as e: #pylint: disable=broad-except
        print(f"Failed to execute in foreground\n{e}")
        return False

def add_path(dir_name: str, take_priority: bool=True) -> None:
    """
    Add directory to PATH env

    Parameters
    ----------
    dir_name: str
        Directory name/path
    take_priority: bool (default True)
        If true, the directory will be prioritized

    Returns
    -------
    None
    """
    old_path = local.env["PATH"]
    local.env["PATH"] = f"{dir_name}:{old_path}" if take_priority else f"{old_path}:{dir_name}"

def mkdir(*dir_tree) -> None:
    """
    Create directory

    Parameters
    ----------
    *dir_tree
        Directory hierarcy

    Retuns
    ------
    None
    """
    dir_name = path_join(*dir_tree)
    if not os.path.exists(dir_name):
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        if is_exists(dir_name):
            print(f"Directory {dir_name} created successfully")
            return
        print(f"Directory {dir_name} can't be created")
        return
    print(f"Directory {dir_name} already exists, can't create")

def mkdirs(*dirs) -> None:
    """
    Create multiple directiory

    Parameters
    ----------
    *dirs
        Directory

    Returns
    -------
    None
    """
    for current_dir in dirs:
        mkdir(current_dir)

def rmdir(dir_name: str) -> None:
    """
    Remove directory

    Parameters
    ----------
    dir_name: str
        Directory name that you wanna remove

    Returns
    -------
    None
    """
    if not os.path.exists(dir_name):
        print(f"Directory {dir_name} doesn't exist, no need to remove it")
        return
    rmtree(dir_name, ignore_errors=True)
    if is_exists(dir_name):
        print(f"Directory {dir_name} still exists, can't remove")
        return
    print(f"Directory {dir_name} removed successfully")

def rm(*file_tree) -> None:
    """
    Remove file

    Parameters
    ----------
    *file_tree
        File location hierarcy

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
    Check if commands exist

    Parameters
    ----------
    cmd: str
        Command name

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
    Check if required commands exist

    Parameters
    ----------
    *commands
        List of commands

    Returns
    -------
    None
    """
    absent_commands_list = [command for command in commands if not command_exists(command)]
    if absent_commands_list:
        absent = ', '.join(absent_commands_list)
        print(f"Required commands not found: {absent}")
        sys_exit(1)

def clean_all(release_dir: str, target_dir: str) -> None:
    """
    Clean all build file

    Parameters
    ----------
    release_dir: str
        Release directory
    target_dir: str
        Target directory

    Returns
    -------
    None
    """
    print("Cleaning started")
    rmdir(release_dir)
    rmdir(target_dir)
    print("Cleaning finished")

def make(threads: int, *args, **kwargs) -> None:
    """
    Make command

    Parameters
    ----------
    threads: int
        How many threads
    *args
        Will be passed to fg function
    **kwargs
        Will be passed to fg function

    Returns
    -------
    None
    """
    print("Running make...")
    if not fg("make", f"-j{threads}", *args, **kwargs):
        sys_exit(1)
    print("Make done.")

def install(*args, **kwargs) -> None:
    """
    Make install

    Parameters
    ----------
    *args
        Will be passed to fg function
    **kwargs
        Will be passed to fg function

    Returns
    -------
    None
    """
    print("Installing...")
    if not fg("make", "install", *args,  **kwargs):
        sys_exit(1)
    print("Installation done.")

class Builder:
    """
    Class to build ffmpeg
    """
    def __init__(self,
            library_data: dict,
            os_type: str,
            target_dir: str="targets",
            release_dir: str="release",
            bin_dir: str="bin",
        ):
        self.__dir_data={
            "target_dir": path_join(CWD(), target_dir),
            "release_dir": path_join(CWD(), release_dir),
            "bin_dir": path_join(CWD(), release_dir, bin_dir),
            "pkg_config_path": path_join(CWD(), release_dir, "lib", "pkgconfig")
        }
        self.__ffmpeg_opts = []

        #Value will filled at build function
        self.__event={
                'pre_dependency': self.__pre_dependency,
                'post_download': self.__post_download,
                'pre_configure': self.__pre_configure,
                'post_configure': self.__post_configure,
                'post_install': self.__post_install,
            }
        self.__library_data=library_data
        self.__is_slavery=False
        self.__is_static_ffmpeg=False
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
            Return release dir
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

    def __add_ffmpeg_lib(self, lib: str) -> None:
        """
        Add enabled library to ffmpeg configuration

        Parameters
        ----------
        lib: str
            Library name
        """
        if lib in ('libogg', 'libsdl', "libudfread"):
            return
        if lib == 'libopencore':
            self.__library_data['ffmpeg']['configure_opts'].extend([
                "--enable-libopencore_amrnb",
                "--enable-libopencore_amrwb"
            ])
            return
        #Cuurrenty an issue in libvmaf also requires FFmpeg to be built with --ld="g++" for a static build to succeed.
        if lib == 'libvmaf':
            self.__library_data['ffmpeg']['configure_opts'].append("--ld=g++")
        self.__library_data['ffmpeg']['configure_opts'].append(f"--enable-{lib}")
        return

    def __configuration_handler(self, threads: int, silent: bool, library: str) -> bool:
        """
        Handle library configuration

        Parameters
        ----------
        threads: int
            Parallel jobs for make command
        silent: bool
            Verbose or not
        library: str
            Library name

        Returns
        -------
        bool
        """
        if library == "ffmpeg-windows-deps-master":
            fg("cp", "-f", "./*", f"{self.release_dir}/bin")
            return True
        if library == 'ffnvcodec':
            install(f"PREFIX={self.release_dir}", silent=silent)
            return True
        if library == "libass":
            with local.env(
                CFLAGS=f"{local.env.get('CFLAGS', '')} -I{self.release_dir}/include/harfbuzz",
                ):
                    self.configure(*self.__library_data[library].get("configure_opts", []), silent=silent)
                    return False
        if library == 'libx264' and self.is_linux:
            with local.env(CXXFLAGS="-fPIC"):
                self.configure(*self.__library_data['libx264'].get("configure_opts", []), silent=silent)
                return False
        if library == 'openssl':
            if not fg("bash",
                "./config",
                *self.__library_data['openssl'].get("configure_opts", [])):
                sys_exit(1)
            make(threads, silent=silent)
            fg("make", "install_sw", f"-j{threads}")
            return True
        if library == 'zlib':
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
                    make(threads, "-f", "./win32/Makefile.gcc")
                    install("-f", "./win32/Makefile.gcc")
                    return True
            self.configure(*self.__library_data['zlib'].get("configure_opts", []), silent=silent)
            make(threads, silent=silent)
            install(silent=silent)
            return True

        if self.__library_data[library].get("configuration", "configure") == "meson":
            self.meson(*self.__library_data[library].get("configure_opts", []), silent=silent)
            fg("ninja", "-j", threads, silent=silent)
            fg("ninja", "install")
            return True
        if self.__library_data[library].get("configuration", "configure") == "cmake":
            self.cmake(*self.__library_data[library].get("configure_opts", []), silent=silent)
            return False
        self.configure(*self.__library_data[library].get("configure_opts", []), silent=silent)
        return False

    def __pre_dependency(self, lib: str) -> None:
        """
        This function will executed before dependency check

        Parameters
        ----------
        lib: str
            Library name

        Returns
        -------
        None
        """
        if lib == 'harfbuzz':
            if 'libfreetype' in self.__targets:
                self.__library_data['harfbuzz']['configure_opts'].append("--with-freetype=yes")
                self.__library_data['harfbuzz']["dependencies"]=['libfreetype']
                return
            self.__library_data['harfbuzz']['configure_opts'].append("--with-freetype=no")

        elif lib == 'libfreetype':
            if 'zlib' in self.__targets:
                self.__library_data['libfreetype']['configure_opts'].append("--with-zlib=yes")
                self.__library_data['libfreetype']["dependencies"]=['zlib']
                return
            self.__library_data['libfreetype']['configure_opts'].append("--with-zlib=no")

        elif lib == 'libsrt':
            if 'gnutls' in self.__targets:
                self.__library_data['libsrt']["dependencies"]=['gnutls']
                return
            if 'openssl' in self.__targets:
                self.__library_data['libsrt']["dependencies"]=['openssl']
                return

    def __post_download(self, lib: str) -> None:
        """
        This function will executed after download finished

        Parameters
        ----------
        lib: str
            Library name

        Returns
        -------
        None
        """
        if lib in ["libaom", "libdav1d", "libopenh264"]:
            mkdir(self.target_dir, self.__library_data[lib]['folder_name'])

        elif lib in ["libgme", "libopenjpeg"]:
            mkdir(self.target_dir, *self.__library_data[lib]['folder_name'])

    def __pre_configure(self, lib: str) -> None:
        """
        This function will executed before configure

        Parameters
        ----------
        lib: str
            Library name

        Returns
        -------
        None
        """
        if lib == 'cmake':
            rm("Modules", "FindJava.cmake")
            (local["perl"][ "-p", "-i", "-e", "s/get_filename_component.JNIPATH/#get_filename_component(JNIPATH/g", "Tests/CMakeLists.txt"])()

        elif lib == 'ffmpeg':
            cflags_extra=" -static -static-libstdc++ -static-libgcc " if self.__is_static_ffmpeg else ''
            ldflags_extra=" -static -static-libstdc++ -static-libgcc " if self.__is_static_ffmpeg else ''
            self.__library_data['ffmpeg']['configure_opts'].extend([
                *self.__ffmpeg_opts,
                # f"--bindir={self.path_fixer(self.release_dir)}/bin"
                # f"--libdir={self.path_fixer(self.release_dir)}/lib",
                f"--pkgconfigdir={self.path_fixer(self.release_dir)}/lib/pkgconfig",
                f"--extra-cflags=-I{self.path_fixer(self.release_dir)}/include {cflags_extra}",
                f"--extra-ldflags=-L{self.path_fixer(self.release_dir)}/lib -fstack-protector {ldflags_extra}"
            ])
            if self.__is_static_ffmpeg:
                self.__library_data['ffmpeg']['configure_opts'].extend(["--extra-cxxflags=-static -static-libstdc++ -static-libgcc ","--extra-libs=-ldl -lrt -lpthread"])

            for ffmpeg_lib in self.__library_data:
                if ffmpeg_lib.startswith("lib") or ffmpeg_lib in ("gmp", "openssl", "zlib", "ffnvcodec"):
                    if ffmpeg_lib in self.__targets:
                        self.__add_ffmpeg_lib(ffmpeg_lib)

            if 'libsdl' in self.__targets:
                self.__library_data['ffmpeg']['configure_opts'].append('--enable-ffplay')

            if not self.__is_slavery and 'gnutls' in self.__targets:
                print("Applying free replacements for non-free components")
                self.__library_data['ffmpeg']['configure_opts'].append("--enable-gnutls")

            elif self.__is_slavery:
                print_lines("You are applying dirty non-free attachments. Are you sure you need this?",
                        "Now you can't distribute this FFmpeg build to anyone, so it's almost useless in real products.",
                        "You can't sell or give away these files")
                print()
                self.__library_data['ffmpeg']['configure_opts'].append("--enable-nonfree")
                    # Non-free unfortunately
                    # Should be replaced with gnutls
                    # http://www.iiwnz.com/compile-ffmpeg-with-rtmps-for-facebook
                    # libfdk_aac is incompatible with the gpl and --enable-nonfree is not specified.
                        # https://trac.ffmpeg.org/wiki/Encode/AAC

            # Unfortunately even creators of MSYS2 can't build it with --enable-pthreads :(
            # https://github.com/msys2/MINGW-packages/blob/master/mingw-w64-ffmpeg/PKGBUILD
            if not self.is_windows:
                self.__library_data['ffmpeg']['configure_opts'].extend(["--extra-libs=-lpthread", "--enable-pthreads"])
            if 'libsoxr' in self.__targets:
                self.__library_data['ffmpeg']['configure_opts'].append("--extra-libs=-lgomp")

        elif lib == "libaom":
            # TODO: Don't forget about different kinds of cmake (msys/cmake and mingw/cmake)
            self.__library_data['libaom']['configure_opts'].append(f"{self.target_dir}/aom")

        elif lib == 'libbluray':
            fg("autoreconf", "-fiv")

        elif lib == 'libdav1d':
            self.__library_data['libdav1d']['configure_opts'].extend([f"--libdir={self.release_dir}/lib", f"{self.target_dir}/dav1d-{re_findall('dav1d-(.+).tar', self.__library_data['libdav1d']['download_opts'][1])[0]}"])

        elif lib == 'libfdk-aac':
            fg("autoreconf", "-fiv")

        elif lib == 'libopenh264':
            self.__library_data['libopenh264']['configure_opts'].extend([f"--libdir={self.release_dir}/lib",f"{self.target_dir}/openh264-{re_findall('libopenh264-(.+).tar', self.__library_data['libopenh264']['download_opts'][1])[0]}"])

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
                    return
                local.env["LDFLAGS"] = " -fstack-protector"

        elif lib == 'libsrt':
            if 'openssl' in self.__targets:
                self.__library_data['libsrt']['configure_opts'].append("-DOPENSSL_USE_STATIC_LIBS=on")
                return
            if 'gnutls' in self.__targets:
                self.__library_data['libsrt']['configure_opts'].append("-DUSE_ENCLIB=gnutls")
                return
            self.__library_data['libsrt']['configure_opts'].append("-DENABLE_ENCRYPTION=off")

        elif lib == 'libtheora':
            print("Removing --fforce-adr from configure")
            ((local["sed"]["s/-fforce-addr//g", "configure"]) > "configure.patched") & FG #pylint: disable=pointless-statement
            fg("chmod", "+x", "configure.patched")
            fg("mv", "configure.patched", "configure")
            print("Configure processing done.")
            self.__library_data['libtheora']['configure_opts'].extend([
                f"--with-ogg-libraries={self.release_dir}/lib",
                f"--with-ogg-includes={self.release_dir}/include/",
                f"--with-vorbis-libraries={self.release_dir}/lib",
                f"--with-vorbis-includes={self.release_dir}/include/"
            ])

        elif lib == 'libudfread':
            fg("autoreconf", "-fiv")

        elif lib == 'libvmaf':
            self.__library_data['libvmaf']['configure_opts'].append(f"--libdir={self.release_dir}/lib")

        elif lib == 'libvorbis':
            self.__library_data['libvorbis']['configure_opts'].extend([
                f"--with-ogg-libraries={self.path_fixer(self.release_dir)}/lib",
                f"--with-ogg-includes={self.path_fixer(self.release_dir)}/include"
            ])

        elif lib == "libvpx" and self.is_mac:
            print("Patching libvpx for MacOS")
            ((local["sed"]["s/,--version-script//g", "build/make/Makefile"]) > "build/make/Makefile.patched")()
            ((local["sed"]["s/-Wl,--no-undefined -Wl,-soname/-Wl,-undefined,error -Wl,-install_name/g",
                "build/make/Makefile.patched"]) > "build/make/Makefile")()

        elif lib == 'libzimg':
            fg("autoreconf", "-fiv")

        elif lib == 'openssl':
            self.__library_data['openssl']['configure_opts'].extend([
                f"--prefix={self.path_fixer(self.release_dir)}",
                f"--openssldir={self.path_fixer(self.release_dir)}",
                f"--with-zlib-include={self.path_fixer(self.release_dir)}/include/",
                f"--with-zlib-lib={self.path_fixer(self.release_dir)}/lib",
                "no-shared",
                "zlib"
            ])

        elif lib == 'pkg-config':
            self.__library_data['pkg-config']['configure_opts'].append(f"--with-pc-path={self.release_dir}/lib/pkgconfig")

    def __post_configure(self, lib: str) -> None:
        """
        This function will executed after configuring

        Parameters
        ----------
        lib: str
            Library name

        Returns
        -------
        None
        """
        if lib == "libmp3lame":
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

        elif lib == "libxvid":
            file=path_join(self.target_dir, "xvidcore", "build", "generic" ,"Makefile")
            start=findText(file, "ifeq ($(SHARED_EXTENSION),dll)")
            end=findText(file, "$(LN_S) $(SHARED_LIB) $(DESTDIR)$(libdir)/$(SO_LINK)")+1
            delete_lines(file, start, end)

    def __post_install(self, lib: str):
        """
        This function will executed after installing

        Parameters
        ----------
        lib: str
            Library name

        Returns
        -------
        None
        """
        if lib == 'gnutls':
            #Fix static linking issue
            with open(f"{self.release_dir}/lib/pkgconfig/gnutls.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.release_dir}/lib/pkgconfig/gnutls.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("Libs: -L${libdir} -lgnutls", "Libs: -L${libdir} -lgnutls -ltasn1 -lgmp -lunistring -lnettle -lhogweed"))

        elif lib == "libgme":
            #Fix static linking issue
            with open(f"{self.release_dir}/lib/pkgconfig/libgme.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.release_dir}/lib/pkgconfig/libgme.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("Libs.private: -lstdc++ -lz", "Libs.private: -lstdc++ -lz -lubsan -ldl -lrt"))

        elif lib == "libsrt":
            #Fix gcc_s not found
            with open(f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/srt.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/srt.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("-lgcc_s", ""))

        elif lib == 'libx265':
            ((local["sed"][
                "s/-lx265/-lx265 -lstdc++/g",
                f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc"]
            ) > f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc.tmp")()
            fg("mv", f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc.tmp", f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc")
            #Fix gcc_s not found
            with open(f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.path_fixer(self.release_dir)}/lib/pkgconfig/x265.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("-lgcc_s", ""))

        elif lib == 'nettle':
            #Fix static linking issue
            with open(f"{self.release_dir}/lib/pkgconfig/nettle.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.release_dir}/lib/pkgconfig/nettle.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("Libs: -L${libdir} -lnettle", "Libs: -L${libdir} -lnettle -lgmp"))

        elif lib == 'openssl':
            #Fix static linking issue
            with open(f"{self.release_dir}/lib/pkgconfig/libcrypto.pc", encoding="utf-8") as f:
                value=f.read()
            with open(f"{self.release_dir}/lib/pkgconfig/libcrypto.pc", "w", encoding="utf-8") as f:
                f.write(value.replace("Libs: -L${libdir} -lcrypto", "Libs: -L${libdir} -lcrypto -lz -ldl"))

    def __build_library(self,
            library: str,
            threads: int,
            is_dependency=False,
            silent: bool=False
        ) -> None:
        """
        This function will handle the build process

        Parameters
        ----------
        library: str
            Library name
        threads: int
            How many threads
        is_dependency: bool (default False)
            If the library is needed by other library
        silent: bool (default False)
            Verbose or not

        Returns
        -------
        None
        """
        if not self.is_needed(library) and not is_dependency:
            return
        self.__event['pre_dependency'](library)
        if len(self.__library_data[library].get('dependencies', [])) != 0:
            for dependency in self.__library_data[library]['dependencies']:
                if not self.is_already_build(dependency):
                    self.__build_library(dependency, threads, is_dependency=True)

        self.download(*self.__library_data[library]['download_opts'])
        self.__event['post_download'](library)
        with self.target_cwd(*self.__library_data[library]['folder_name'] if isinstance(self.__library_data[library]['folder_name'], list) else [self.__library_data[library]['folder_name']]):
            self.__event['pre_configure'](library)
            if not self.__configuration_handler(threads, silent, library):
                self.__event['post_configure'](library)
                make(threads, silent=silent)
                install(silent=silent)
            self.__event['post_install'](library)
            self.mark_as_built(library)

    def build(self,
            targets: list,
            threads: Optional[int]=None,
            is_slavery_mode: bool=False,
            is_static_ffmpeg: bool=False,
            extra_cflags: str="",
            extra_ldflags: str="",
            extra_libs: str="",
            extra_ffmpeg_args: str="",
            **kwargs
        ) -> None:
        """
        Function to start building

        Parameters
        ----------
        targets: list
            List of library that we will build
        threads: Optional[int]
            Number of threads
        is_slavery_mode: bool (default False)
            Is slavery mode
        is_static_ffmpeg: bool (default False)
            Is build static ffmpeg
        extra_cflags: str (default "")
            Extra CFLAGS
        extra_ldflags: str (default "")
            Extra LDFLAGS
        extra_libs: str (default "")
            Extra FFmpeg libs
        extra_ffmpeg_args: str (default "")
            Extra argument to ffmpeg

        Returns
        -------
        None
        """
        extra_cflags=f"-I{self.release_dir}/include {extra_cflags}"
        extra_ldflags=f"-L{self.release_dir}/lib {extra_ldflags}"
        self.__targets=targets
        self.__is_slavery=is_slavery_mode
        self.__is_static_ffmpeg=is_static_ffmpeg
        if threads is None:
            threads = cpu_count(logical=False)
            if self.is_mac:
                self.__ffmpeg_opts.append("--enable-videotoolbox")
        self.__ffmpeg_opts.extend(shlex_split(extra_ffmpeg_args))
        if extra_libs != "":
            self.__ffmpeg_opts.append(f"--extra-libs={extra_libs}")

        print_header("Building process started")
        mkdirs(self.target_dir, self.release_dir)
        add_path(self.bin_dir)

        with local.env(
            CFLAGS=f"{local.env.get('CFLAGS', '')} {extra_cflags}",
            LDFLAGS=f"{local.env.get('LDFLAGS', '')} {extra_ldflags}",
            PKG_CONFIG_LIBDIR=f"{self.path_fixer(self.release_dir)}/lib/pkgconfig"
            ):
            for library in targets:
                self.__build_library(
                    library,
                    threads,
                    **kwargs
                )

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

    def configure(self, *opts, **kwargs) -> None:
        """
        Run configure

        Parameters
        ----------
        *args
            Will passed to configure
        **kwargs
            Will passed to fg function

        Returns
        -------
        None
        """
        configure_options = ("./configure", f"--prefix={self.release_dir}",) + opts
        if self.is_windows:
            configure_options = ("bash",) + configure_options
        fg("chmod", "+x", "./configure")
        print(f"Configure with flags: {configure_options}")
        if not fg(*configure_options, **kwargs):
            sys_exit(1)
        print("Configuring done.")

    def cmake(self, *args, **kwargs) -> None:
        """
        Run CMake

        Parameters
        ----------
        *args
            Will passed to CMake
        **kwargs
            Will passed to fg function

        Returns
        -------
        None
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
        #
        # Don't forget that you can search on Windows without grep -r, using
        # something like " dir -Recurse | Select-String -pattern 'x265.pc'" in Power Shell to find errors like this.
        #
        # Discussion: https://cmake.org/pipermail/cmake/2018-February/067058.html
        # Conversions between paths:
        # https://stackoverflow.com/questions/41492504/how-to-get-native-windows-path-inside-msys-python
        # TODO: implement command line option to switch between versions of CMake, protect with cpp(RELEASE_DIR)

        if not fg("cmake", "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={self.release_dir}", f"-DCMAKE_PREFIX_PATH={self.release_dir}",*args, **kwargs):
            sys_exit(1)
        print("Making with CMake done.")

    def download(self, url: str, dest_name: str, alternative_dir: Optional[str]=None):
        """
        Function to download file

        Parameters
        ----------
        url: str
            Download url
        dest_name: str
            File name
        alternative_dir: Optional[str]
            Custom dir name when extract
        """
        download_path = self.target_dir

        if alternative_dir is not None:
            download_path = path_join(download_path, alternative_dir)
            mkdir(download_path)

        base_path = path_join(download_path, dest_name)
        if is_exists(base_path):
            print(f"Source file already downloaded: {url}")
            return

        print(f"Downloading {url}")
        successful_download = False
        for _ in range(DOWNLOAD_RETRY_ATTEMPTS):
            if fg("curl", "--insecure", "-L", "--silent", "-o", base_path, url) is True:
                successful_download = True
                break
            print(f"Downloading failed: {url}. Retrying in {DOWNLOAD_RETRY_DELAY} seconds")
            sleep(DOWNLOAD_RETRY_DELAY)

        if not successful_download:
            print(f"Failed to download multiple times: {url}")
            sys_exit(1)
        print(f"Successfuly downloaded: {url}")

        if ".tar" in dest_name:
            if fg("tar", "-xvf", self.path_fixer(base_path), "-C", self.path_fixer(download_path), silent=True):
                return
            print(f"Failed to extract {dest_name}")
            sys_exit(1)
        elif ".zip" in dest_name:
            with ZipFile(base_path) as myzip:
                myzip.extractall(download_path)
            return
        raise Exception

    def is_already_build(self, library: str) -> bool:
        """
        Check if library already build

        Parameters
        ----------
        library: str
            The library name

        Returns
        -------
        bool
        """
        return is_exists(path_join(self.target_dir, f"{library}.ok"))

    def is_needed(self, library: str) -> bool:
        """
        Check if library need to build or not

        Parameters
        ----------
        library: str
            The library name

        Returns
        -------
        bool
        """
        if library not in self.__targets:
            return False
        if library == "ffmpeg-msys2-deps" and not self.is_windows:
            return False

        print(f"\nBuilding target: {library}\n{ITALIC_SEPARATOR}")
        if self.is_already_build(library):
            print_block("Cached version found")
            return False
        print("No cache, needs building")
        return True

    def mark_as_built(self, library: str) -> None:
        """
        Mark if the library has been build

        Parameters
        ----------
        library: str
            The library name

        Returns
        -------
        None
        """
        filename = path_join(self.target_dir, f"{library}.ok")
        print_block(f"Creating a lock file: {filename}")
        with open(filename, "w", encoding="utf-8") as _:
            pass

    def meson(self, *args, **kwargs) -> None:
        """
        Run meson

        Parameters
        ----------
        *args
            Will passed to meson
        **kwargs
            Will passed to fg function

        Returns
        -------
        None
        """
        meson_flags=("meson", "setup", f"--prefix={self.release_dir}",) + args
        print(f"Configuring with meson\nFlags: {meson_flags}")
        if not fg(*meson_flags, **kwargs):
            sys_exit(1)
        print("Configure with meson done...")

    def path_fixer(self, src: str) -> str:
        """
        Fix windows path

        Parameters
        ----------
        src: str
            Path

        Returns
        -------
        str
            Fixed path

        Raises
        ------
        NotImplementedError
            Raised if continuing without properly parsed path

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

        Parameters
        ----------
        *dirs
            List of directories
        """
        result_dir=self.target_dir
        for curr_dir in dirs:
            result_dir = path_join(result_dir, curr_dir)
        return local.cwd(result_dir)

def main() -> None:
    """
    Program Entry Point

    Returns
    -------
    None
    """
    parser = ArgumentParser(description='Build a special edition of FFMPEG.')
    parser.add_argument('-j', '--jobs', metavar='int', action="store", dest="jobs", type=int, help='Number of parallel jobs', default=None)
    parser.add_argument('-b', '--build', action="store_true", dest="build_mode", help='Run build')
    parser.add_argument('-c', '--clean', action="store_true", dest="clean_mode", help='Clean solution')
    parser.add_argument('-q', '--silent', action="store_true", dest="silent_mode", help='Disable build debug')
    parser.add_argument('--targets', action="store", dest="targets",
        help='comma-separated targets for building (empty = build all)')
    parser.add_argument('--exclude-targets', action="store", dest="exclude_targets", help='Don\'t build these')
    parser.add_argument('--extra-cflags', metavar='string', dest="extra_cflags", help='Build extra CFLAGS', default="")
    parser.add_argument('--extra-ldflags', metavar='string', dest="extra_ldflags", help='Build extra LDFLAGS', default="")
    parser.add_argument('--extra-libs', metavar='string', dest="extra_libs", help='FFmpeg extra LIBS', default="")
    parser.add_argument('--extra-ffmpeg-args', metavar='string', dest='ffmpeg_args', help='Extra FFmpeg argument', default="")
    parser.add_argument('--target-dir', metavar='dir', default="targets", help="Target directory")
    parser.add_argument('--release-dir', metavar='dir', default="release", help="Release directory")
    parser.add_argument('--disable-ffplay', dest="disable_ffplay", action='store_true', help="Disable building ffplay", default=False)
    parser.add_argument('--static-ffmpeg', dest="static_ffmpeg", action='store_true', help="Build static ffmpeg (-static, etc)", default=False)
    parser.add_argument('--use-nonfree-libs', dest="slavery_mode", action='store_true', help="Use non-free libraries", default=False)
    parser.add_argument('--use-system-build-tools', dest="default_tools", action='store_true', help="Use cmake, nasm, yasm, pkg-config that installed on system", default=False)
    args = parser.parse_args()

    targets=['cmake', 'ffnvcodec', 'gmp', 'gnutls', 'libaom', 'libass', 'libbluray', 'libdav1d', 'libfdk-aac', 'libfontconfig', 'libfreetype',
             'libfribidi', 'libgme', 'libkvazaar', 'libmp3lame', 'libogg', 'libopus', 'libopencore', 'libopenh264', 'libopenjpeg', 'libsdl', 'libshine', 'libsoxr', 'libsrt',
             'libsvtav1', 'libtheora', 'libvidstab', 'libvmaf', 'libvorbis', 'libvpx', 'libx264', 'libx265', 'libxvid',
             'libzimg', 'nasm', 'openssl', 'pkg-config', 'yasm', 'zlib', 'ffmpeg-msys2-deps', 'ffmpeg'
            ]
    #Check if user specify specific targets
    targets = [_ for _ in args.targets.split(",") if _ in targets] if args.targets is not None else targets
    #Check if user exclude some targets
    targets = [x for x in targets if x not in args.exclude_targets.split(",") ] if args.exclude_targets is not None else targets
    #Remove cmake, yasm, nasm, and pkg-config from targets if user dont wanna compile it
    targets = [x for x in targets if x not in ('cmake', 'pkg-config', 'nasm', 'yasm')] if args.default_tools else targets
    if not args.slavery_mode:
        #Remove libfdk-aac and openssl if not in slavery mode
        for target in ('libfdk-aac', 'openssl'):
            try:
                targets.remove(target)
            except ValueError:
                continue
    elif args.slavery_mode:
        #Remove gnutls if in slavery mode
        try:
            targets.remove('gnutls')
        except ValueError:
            pass
    if 'libsdl' in targets and args.disable_ffplay:
        targets.remove('libsdl')
    if not bool(command_exists("meson") and command_exists("ninja")):
        if any(_ in targets for _ in ("libopenh264", "libdav1d")):
            print("In order to build libopenh264 or libdav1d, you must install meson and ninja in your system")
            sys_exit(1)

    print_block("Hello, slave, how are you?" if args.slavery_mode else "Building FFmpeg, free as in freedom!")
    print_header("Processing targets:")
    print_block(str(targets))

    if args.build_mode:
        require_commands("autoconf", 'curl', 'gperf', 'libtoolize', 'make', 'tar',*['cmake', 'nasm', 'yasm', 'pkg-config'] if args.default_tools else [])
        os_type=system()
        kwargs={}
        if args.jobs is not None:
            kwargs={"threads": args.jobs}
        with open("libraries.json", encoding="utf-8") as f:
            Builder(load(f), os_type, target_dir=args.target_dir, release_dir=args.release_dir).build(
                targets,
                is_slavery_mode=args.slavery_mode,
                is_static_ffmpeg=args.static_ffmpeg,
                silent=args.silent_mode,
                extra_cflags=args.extra_cflags,
                extra_ldflags=args.extra_ldflags,
                extra_libs=args.extra_libs,
                extra_ffmpeg_args=args.ffmpeg_args,
                **kwargs
            )

    if args.clean_mode:
        clean_all(args.target_dir, args.release_dir)

    print("OpenStreamCaster's FFmpeg-builder finished its work. And you?\nSee help for more information")

if __name__ == '__main__':
    import re
    import os
    from time import sleep
    from pathlib import Path
    from zipfile import ZipFile
    from argparse import ArgumentParser
    from os import getcwd as CWD
    from os.path import exists as is_exists, join as path_join
    from platform import system
    from shutil import rmtree
    from re import findall as re_findall
    from sys import exit as sys_exit
    from json import load

    try:
        from plumbum import local, FG, CommandNotFound
        from psutil import cpu_count
        from shlex import split as shlex_split
    except ModuleNotFoundError:
        print("Install required module with `pip install -r requirements.txt`")
        sys_exit(1)

    main()
