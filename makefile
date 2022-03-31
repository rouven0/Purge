install:
	@echo Setting up the virtual environment...
	@python3 -m venv venv
	@echo Installing requirements...
	@venv/bin/pip install -r requirements.txt
	@echo Done.
	@echo Setting up the systemd service...
	@sed -i 's|WORKINGDIRECTORY|'$(PWD)'|g' Purge.service
	@sed -i 's|USER|'$(USER)'|g' Purge.service
	@sudo cp ./Purge.service /etc/systemd/system
	@sudo systemctl daemon-reload
	@sudo systemctl enable Purge.service
	@echo Done. The service is ready to be started

uninstall:
	@echo Removing systemd service...
	@sudo systemctl disable Purge.service
	@sed -i 's|'$(PWD)'|WORKINGDIRECTORY|g' Purge.service
	@sed -i 's|'$(USER)'|USER|g' Purge.service
	@sudo rm /etc/systemd/system/Purge.service
	@sudo systemctl daemon-reload
	@echo Done.

start:
	@sudo systemctl start Purge.service
	@echo Service started

stop:
	@sudo systemctl stop Purge.service
	@echo Service stopped
