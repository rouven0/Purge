{
  description = "The Purge Discord bot";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (system: {
        default = pkgs.${system}.python310Packages.callPackage ./default.nix { };
      });
      nixosModules.default = import ./module.nix;

      devShells = forAllSystems (system: {
        default =
          let
            pythonEnv = pkgs.${system}.python3.withPackages (p: with p; [ gunicorn (self.packages.${system}.default) ]);
          in

          pkgs.${system}.mkShell {
            packages = [ pythonEnv ];
            shellHook = ''
              export PYTHONPATH="${pythonEnv}/bin/python"
            '';
          };
      });
    };
}
