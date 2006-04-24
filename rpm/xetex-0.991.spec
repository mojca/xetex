# # # # # # # # # #
# PREAMBLE
# # # # # # # # # #

Summary: An extension of TeX (and LaTeX/ConTeXt) with Unicode and OpenType support
Name: xetex
Icon: xetex.xpm
Version: 0.991
Release: 1
Copyright: CPL
Group: Productivity/Publishing/TeX/Base
Source: http://scripts.sil.org/svn-view/xetex/TAGS/xetex-%{version}.tar.gz
URL: http://scripts.sil.org/xetex
Vendor: SIL International
Packager: Jonathan Kew <jonathan_kew@sil.org>

# not sure if the tetex version *really* needs to be 3.0 for xetex, but let's be safe...
# setup of older versions might be different enough to break things for us
Requires: tetex >= 3.0

# te_latex is required because we intend to build a xelatex format during installation
Requires: te_latex >= 3.0

# we also need fontconfig, freetype2 and ImageMagick libraries
Requires: fontconfig, freetype2, ImageMagick

# finally, we need the xdvipdfmx driver to be present
Requires: xdvipdfmx

# to build, we need flex, bison, and various -devel packages...
BuildRequires: flex, bison
BuildRequires: fontconfig-devel, freetype2-devel, ImageMagick-devel

%description
XeTeX extends the TeX typesetting system (and macro packages
such as LaTeX and ConTeXt) to have native support for the
Unicode character set, including complex Asian scripts, and
for OpenType and TrueType fonts.

# # # # # # # # # #
# PREP
# # # # # # # # # #

%prep

# setup macro does standard clean-and-unpack
%setup

# # # # # # # # # #
# BUILD
# # # # # # # # # #

%build
sh ./build-xetex

# # # # # # # # # #
# INSTALL
# # # # # # # # # #

%install

# the makefile from the xetex tarball configuration doesn't know how to
# "make install" properly, so we have a custom script for now
# (eventually, a merge with texlive should lead to this getting fixed)

# this script also creates the xetex-installed-files list
sh ./install-xetex

# update the kpathsearch databases
texhash

# # # # # # # # # #
# CONFIGURATION
# # # # # # # # # #

%post

# we build the format files here, to get language config of the target system
# this is similar to the rebuild-formats script in the xetex tarball,
# but that doesn't get installed from the rpm package
# ensure our entries are present in fmtutil.cnf

fmtutil_cnf=`kpsewhich --format="web2c files" fmtutil.cnf`
if [ "`fgrep -c xetex ${fmtutil_cnf}`" == "0" ]; then
	cat >> ${fmtutil_cnf} <<-__EOT__;

	# XeTeX formats
	xetex	xetex	-	*xetex.ini
	xelatex	xetex	language.dat	*xelatex.ini

	__EOT__
fi

# find the existing tex binary, possibly following a symlink
texbin=`which tex`
if [ -L ${texbin} ]; then
	texbin=`readlink -f ${texbin}`
fi
texbindir=`dirname ${texbin}`

# ensure ${texbindir} is in the PATH so that fmtutil can find new xetex
# (normal usage may rely on a symlink, which doesn't yet exist)
PATH=${texbindir}:$PATH

# use system-wide setup if available
fmtutil=`type -p fmtutil-sys` || fmtutil=`type -p fmtutil`

formats="xetex xelatex"
for f in ${formats}; do
# enable our entries if necessary (in case of pre-existing disabled ones)
	${fmtutil} --enablefmt ${f}
	${fmtutil} --byfmt ${f}
done

# create symlinks for the newly-built formats
texlinks --silent

# # # # # # # # # #
# REMOVAL
# # # # # # # # # #

%postun

# after uninstalling, remove format files and disable entries in fmtutil.cnf
formats="xetex xelatex"
fmtutil=`type -p fmtutil-sys` || fmtutil=`type -p fmtutil`
for f in formats; do
	fmt=`kpsewhich --progname=xetex ${f}.fmt`
	if [ "x${fmt}" != "x" ]; then rm ${fmt}; fi
	if [ "x${fmtutil}" != "x" ]; then ${fmtutil} --disablefmt ${f}; fi
done

# update symlinks and the filename databases
texlinks
texhash

# # # # # # # # # #
# FILE LIST
# # # # # # # # # #

%files -f Work/xetex-installed-files
