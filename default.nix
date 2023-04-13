{ lib, buildPythonPackage, fetchPypi, python310Packages, python, ... }:

buildPythonPackage {
  name = "Purge";
  src = ./app;

  propagatedBuildInputs = with python310Packages; [
    flask
    pyyaml
    gunicorn
    python-i18n
    (buildPythonPackage
      rec {
        pname = "Flask-Discord-Interactions";
        version = "2.1.2";
        propagatedBuildInputs = [
          flask
          requests
          requests-toolbelt
          pynacl
          pytest
          (buildPythonPackage
            rec {
              pname = "quart";
              version = "0.18.4";
              propagatedBuildInputs = [
                flask
                hypercorn
                markupsafe
                blinker
                aiofiles
              ];

              src = fetchPypi {
                inherit pname version;
                sha256 = "wXZvJpzbhdr52me6VBcKv3g5rKlzBNy0zQd46r+0QsY=";
              };
            })
        ];

        src = fetchPypi {
          inherit pname version;
          sha256 = "3jN0RcArARN1nt6pZTPQS7ZglFUE17ZSpLcsOX49gLM=";
        };
      })
  ];

  installPhase = ''
    runHook preInstall
    mkdir -p $out/${python.sitePackages}
    cp -r . $out/${python.sitePackages}/Purge
    runHook postInstall '';

  format = "other";
}
