{
  description = "R, RStudio, tidyverse, Python & Bash development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true; # required for RStudio
        };

        commonRPackages = with pkgs.rPackages; [
          tidyverse
          remotes
          devtools
        ];

        R-with-packages = pkgs.rWrapper.override {
          packages = commonRPackages;
        };

        rstudio-with-packages = pkgs.rstudioWrapper.override {
          packages = commonRPackages;
        };

        isLinux = pkgs.stdenv.isLinux;

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # -- R (all platforms) --
            R-with-packages

            # -- RStudio (Linux only; on macOS install via Homebrew / Posit) --
          ] ++ pkgs.lib.optionals isLinux [
            rstudio-with-packages
          ] ++ [

            # -- Python 3.11 (well-established) --
            pkgs.python311
            pkgs.python311Packages.pip
            pkgs.python311Packages.virtualenv
            pkgs.python311Packages.matplotlib

            # -- Bash --
            pkgs.bash

            # -- Pandoc and LaTeX for rendering the report to PDF --
            pkgs.pandoc
            (pkgs.texliveSmall.withPackages (ps: with ps; [
              collection-latexrecommended
              collection-fontsrecommended
              collection-latexextra
              collection-xetex
            ]))

            # -- Utilities needed for R package compilation / GitHub installs --
            pkgs.git
            pkgs.curl
            pkgs.openssl
            pkgs.cacert
            pkgs.pkg-config
          ];

          # Ensure LOCALE is set (some R/tidyverse operations need it)
          LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";

          shellHook = ''
            # Project-local R library so nix store stays read-only
            export R_LIBS_USER="$PWD/.R/library"
            mkdir -p "$R_LIBS_USER"

            # Install random.cdisc.data from the pharmaverse r-universe
            # (the package is not on CRAN; r-universe resolves all deps)
            if [ ! -d "$R_LIBS_USER/random.cdisc.data" ]; then
              echo "══════════════════════════════════════════════════════════"
              echo "  Installing random.cdisc.data from r-universe …"
              echo "══════════════════════════════════════════════════════════"
              R --quiet --no-save <<'EOF'
            install.packages(
              "random.cdisc.data",
              repos = c(
                "https://insightsengineering.r-universe.dev",
                "https://cloud.r-project.org"
              ),
              lib = Sys.getenv("R_LIBS_USER")
            )
            EOF
            fi

            echo ""
            echo "Environment ready."
            echo "  R          : $(R --version | head -1)"
            echo "  Python     : $(python3 --version)"
            echo "  Bash       : $(bash --version | head -1)"
            echo "  Pandoc     : $(pandoc --version | head -1)"
            echo "  RStudio    : run 'rstudio' to launch"
            echo "  R packages : tidyverse, remotes, devtools, random.cdisc.data"
            echo "  Report     : pandoc report.md -o report.pdf --pdf-engine=xelatex"
            echo ""
          '';
        };
      }
    );
}
