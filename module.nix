{ self, lib, pkgs, config, types, ... }:
let
  cfg = config.services.purge;
  appEnv = pkgs.python3.withPackages (p: with p; [ gunicorn self.packages."x86_64-linux".default ]);
in
{
  options.services.purge = {
    enable = lib.mkEnableOption "Purge";
    environmentFile = lib.mkOption {
      type = types.nullOr types.path;
      default = null;
      description = lib.mdDoc ''
        Environment file as defined in {manpage}`systemd.exec(5)`.
      '';
    };
    listenPort = lib.mkOption {
      type = types.port;
      default = 9100;
      description = lib.mdDoc ''
        Port the app will run on.
      '';
    };
  };

  config = lib.mkIf (cfg.enable) {
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
        ExecStart = "${appEnv}/bin/gunicorn bot:app -b 0.0.0.0:${toString cfg.listenPort} --error-logfile -";
        User = "purge";
        Group = "purge";
        EnvironmentFile = cfg.environmentFile;
      };
    };
  };
}
