{ lib, pkgs, config, ... }:
with lib;
let
  cfg = config.services.purge;
  appEnv = pkgs.python311.withPackages (p: with p; [ gunicorn (pkgs.python311Packages.callPackage ./default.nix { }) ]);
in
{
  options.services.purge = {
    enable = mkEnableOption "Purge";
    domain = mkOption {
      type = types.str;
      description = mdDoc ''
        Domain name the app runs under.
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
    systemd.sockets.purge = {
      wantedBy = [ "sockets.target" ];
      before = [ "nginx.service" ];
      requires = [ "purge.socket" ];
      socketConfig.ListenStream = "/run/purge.sock";
    };
    systemd.services.purge = {
      enable = true;
      after = [ "network.target" ];
      environment = {
        DISCORD_CLIENT_ID = cfg.discord.clientId;
        DISCORD_PUBLIC_KEY = cfg.discord.publicKey;
      };
      serviceConfig = {
        DynamicUser = true;
        LoadCredential = "discord-token:${cfg.discord.tokenFile}";
        ExecStart = "${appEnv}/bin/gunicorn purge:app -b /run/purge.sock --error-logfile -";
      };
    };

    services.nginx.virtualHosts."${cfg.domain}" = {
      enableACME = true;
      forceSSL = true;
      proxyPass = "http://unix:/run/purge.sock";
    };

  };
}
