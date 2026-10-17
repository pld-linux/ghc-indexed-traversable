#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	indexed-traversable
Summary:	FunctorWithIndex, FoldableWithIndex, TraversableWithIndex
Name:		ghc-%{pkgname}
Version:	0.1.4
Release:	1
License:	BSD
Group:		Development/Languages
#Source0Download: https://hackage.haskell.org/package/indexed-traversable
Source0:	https://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	ecfacc9a29b750193c0705abde165d4d
URL:		https://hackage.haskell.org/package/indexed-traversable
# Hackage revision 2 of the .cabal file (relaxed dependency bounds)
Source1:	https://hackage.haskell.org/package/%{pkgname}-%{version}/revision/2.cabal?/%{pkgname}-%{version}-r2.cabal
# Source1-md5:	4d702225a59efd843f838be08de6ffda
BuildRequires:	ghc
%if %{with prof}
BuildRequires:	ghc-prof
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
This package provides three useful generalizations:

@ class Functor f => FunctorWithIndex i f | f -> i where \  imap :: (i
-> a -> b) -> f a -> f b @

@ class Foldable f => FoldableWithIndex i f | f -> i where \  ifoldMap
:: Monoid m => (i -> a -> m) -> f a -> m @

@ class (FunctorWithIndex i t, FoldableWithIndex i t, Traversable t)
=> TraversableWithIndex i t | t -> i where \  itraverse :: Applicative
f => (i -> a -> f b) -> t a -> f (t b) @

This package contains instances for types in GHC boot libraries. For
some additional instances see [indexed-traversable-
instances](https://hackage.haskell.org/package/indexed-traversable-
instances).

The [keys](https://hackage.haskell.org/package/keys) package provides
similar functionality, but uses (associated) @TypeFamilies@ instead of
@FunctionalDependencies@.

%package prof
Summary:	Profiling %{pkgname} library for GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description prof
Profiling %{pkgname} library for GHC. Should be installed when GHC's
profiling subsystem is needed.

%prep
%setup -q -n %{pkgname}-%{version}

cp -p %{SOURCE1} %{pkgname}.cabal

# tarball ships no Setup script
echo 'import Distribution.Simple; main = defaultMain' > Setup.hs

%build
runhaskell Setup.hs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.hs build

runhaskell Setup.hs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/lib/package.conf.d

runhaskell Setup.hs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
rm -rf %{name}-%{version}-doc
%{__mv} $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc

runhaskell Setup.hs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/lib/package.conf.d/%{pkgname}.conf

# the library directory name contains an ABI hash, so build the file lists
pkgdir=$(echo $RPM_BUILD_ROOT%{_libdir}/*-linux-%{ghcdir}/%{pkgname}-%{version}-*)
find $pkgdir -type d | sed -e "s|^$RPM_BUILD_ROOT|%dir |" > %{name}.files
find $pkgdir -type f ! -name '*_p.a' ! -name '*.p_hi' | sed -e "s|^$RPM_BUILD_ROOT||" >> %{name}.files
find $pkgdir -type f \( -name '*_p.a' -o -name '*.p_hi' \) | sed -e "s|^$RPM_BUILD_ROOT||" > %{name}-prof.files

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files -f %{name}.files
%defattr(644,root,root,755)
%doc Changelog.md LICENSE %{name}-%{version}-doc/html
%{_libdir}/%{ghcdir}/lib/package.conf.d/%{pkgname}.conf
%dir %{_libdir}/*-linux-%{ghcdir}
%{_libdir}/*-linux-%{ghcdir}/libHS%{pkgname}-%{version}-*.so

%if %{with prof}
%files prof -f %{name}-prof.files
%defattr(644,root,root,755)
%endif
