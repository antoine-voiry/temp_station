@echo off
set v_params=%*
set v_params=%v_params:\=/%
set v_params=%v_params:c:=/mnt/c%
set v_params=%v_params:"=\"%
bash.exe -c "/home/avoiry/.local/share/virtualenvs/temp-and-humidity-cysFBGEl/bin/pylint %v_params%"
