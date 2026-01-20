{
  description = "The Purge Discord bot";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (system: {
        default = pkgs.${system}.python3Packages.callPackage ./default.nix { };
      });
      hydraJobs = forAllSystems (system: {
        default = self.packages.${system}.default;
      });
      nixosModules.default = import ./module.nix;
    };
}
