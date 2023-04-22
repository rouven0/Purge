{ self, lib, pkgs, config, ... }:
with lib;
let
  cfg = config.services.purge;
  appEnv = pkgs.python3.withPackages (p: with p; [ gunicorn (pkgs.python310Packages.callPackage ./default.nix { }) ]);
in
{
  options.services.purge = {
    enable = mkEnableOption "Purge";
    environmentFile = mkOption {
      type = types.nullOr types.path;
      default = null;
      description = mdDoc ''
        Environment file as defined in {manpage}`systemd.exec(5)`.
      '';
    };
    listenPort = mkOption {
      type = types.port;
      default = 9100;
      description = mdDoc ''
        Port the app will run on.
      '';
    };
  };

  config = mkIf (cfg.enable) {
    users.users.purge = {
      isSystemUser = true;
      group = "purge";
    };
    users.groups.purge = { };

    systemd.services.purge = {
      enable = true;
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        ExecStart = "${appEnv}/bin/gunicorn purge:app -b 0.0.0.0:${toString cfg.listenPort} --error-logfile -";
        User = "purge";
        Group = "purge";
        EnvironmentFile = cfg.environmentFile;
      };
    };
  };
}