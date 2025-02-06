{
  description = "Flake-parts based Python project with devenv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devenv.url = "github:cachix/devenv";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
    allowUnfree = true;
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devenv.flakeModule
      ];
      systems = [ "x86_64-linux" "i686-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];

      perSystem = { config, self', inputs', pkgs, system, lib, ... }: {
        packages.default = pkgs.git;

        devenv.shells.default = {
          name = "python-project";

          languages.python = {
            enable = true;
          };

          pre-commit.hooks = {
            treefmt = {
              enable = true;
              package = pkgs.treefmt2;
              settings = {
                formatters = [
                  pkgs.nixpkgs-fmt
                  pkgs.mdformat
                  pkgs.taplo # TOML - primarily just for the treefmt config files
                  pkgs.typos
                ];
              };
            };
          };

          packages = with pkgs; [
            config.packages.default
            python3Packages.pip
            rye
            just
            ungoogled-chromium # TODO: Update Chromium version to 133 when available in nixpkgs
          ];
        };
      };
    };
}
