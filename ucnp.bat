@echo off
call activate ucnp
set PYTHONPATH=%PYTHONPATH%;C:\ucnp\pyucnp-master
python start_app.py %*