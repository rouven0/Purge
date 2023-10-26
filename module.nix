{ lib, pkgs, config, ... }:
with lib;
let
  cfg = config.services.purge;
  appEnv = pkgs.python311.withPackages (p: with p; [ gunicorn (pkgs.python311Packages.callPackage ./default.nix { }) ]);
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
    systemd.services.purge = {
      enable = true;
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      environment = {
        DISCORD_CLIENT_ID = cfg.discord.clientId;
        DISCORD_PUBLIC_KEY = cfg.discord.publicKey;
      };
      serviceConfig = {
        DynamicUser = true;
        LoadCredential = "discord-token:${cfg.discord.tokenFile}";

        ExecStart = "${appEnv}/bin/gunicorn purge:app -b 0.0.0.0:${toString cfg.listenPort} --error-logfile -";
      };
    };
  };
}
