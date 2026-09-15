HELA JYOTISHYA V3.5.1 - PHKS Creation

Fix: packaged Windows EXE now explicitly includes Python SQLite runtime (_sqlite3).
The build process also runs the final EXE in a packaging self-test before creating Setup.exe.
If that test fails, the installer will not be produced.

Use: double-click BUILD_INSTALLER.cmd.
Customer receives only the final Setup.exe from the release folder.
