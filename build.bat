pyinstaller --clean -y -w -F -i "mainicon.ico" --add-data "mainicon.png;." main.py
rd /s /q .\build