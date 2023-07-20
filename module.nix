{ lib, pkgs, config, ... }:
with lib;
let
  cfg = config.services.purge;
  appEnv = pkgs.python3.withPackages (p: with p; [ gunicorn (pkgs.python310Packages.callPackage ./default.nix { }) ]);
in
{
  options.services.purge = {
    enable = mkEnableOption "Purge";
    listenPort = mkOption {
      type = types.port;
      default = 9100;
      description = mdDoc ''
        Port the app will run on.
      '';
    };
    discord = {
      clientId = mkOption {
        type = types.str;
        description = mdDoc ''
          Client id to use with Discord. 
        '';
      };
      publicKey = mkOption {
        type = types.str;
        description = mdDoc ''
          Public key to verify requests.
        '';
      };
      tokenFile = mkOption {
        type = types.path;
        default = null;
        description = mdDoc ''
          File containing the Bot Token to authenticate to Discord.
        '';
      };

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
      environment = {
        DISCORD_CLIENT_ID = cfg.discord.clientId;
        DISCORD_PUBLIC_KEY = cfg.discord.publicKey;
        TOKEN_FILE = cfg.discord.tokenFile;
      };
      serviceConfig = {
        ExecStart = "${appEnv}/bin/gunicorn purge:app -b 0.0.0.0:${toString cfg.listenPort} --error-logfile -";
        User = "purge";
        Group = "purge";
      };
    };
  };
}
