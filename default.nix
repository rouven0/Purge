{ buildPythonPackage, fetchPypi, flask, pyyaml, gunicorn, python-i18n, requests, requests-toolbelt, pynacl, pytest, python, setuptools, ... }:

buildPythonPackage {
  name = "Purge";
  src = ./purge;

  propagatedBuildInputs = [
    flask
    pyyaml
    gunicorn
    python-i18n
    (buildPythonPackage
      rec {
        pname = "Flask-Discord-Interactions";
        version = "2.1.2";
        pyproject = true;
        build-system = [ setuptools ];
        # skip the tests since they require quart
        doCheck = false;
        propagatedBuildInputs = [
          flask
          requests
          requests-toolbelt
          pynacl
          pytest
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
    cp -r . $out/${python.sitePackages}/purge
    runHook postInstall '';

  shellHook = "export FLASK_APP=purge";

  format = "other";
}
