GOTO:MAIN

:cargoReleaseBuild
    SETLOCAL ENABLEDELAYEDEXPANSION
        cargo clean
        cargo build --release --no-default-features -F %~1
        set features=%~1
        set cleaned_features=%features:,=-%
        COPY target\release\wicked_waifus_win.dll build\%~2\wicked-waifus-win-%cleaned_features%.dll
        cargo clean
    ENDLOCAL
EXIT /B 0

:buildAllVariants
    SETLOCAL ENABLEDELAYEDEXPANSION
        call:cargoReleaseBuild "cn_beta_2_6_0,%~1" %~1
        call:cargoReleaseBuild "os_beta_2_6_0,%~1" %~1
        : call:cargoReleaseBuild "os_live_2_2_0,%~1" %~1
    ENDLOCAL
EXIT /B 0

:MAIN
if exist "build" rd /q /s "build"
mkdir build
mkdir build\regular
mkdir build\only-sig-bypass
cargo clean

call:buildAllVariants regular
call:buildAllVariants only-sig-bypass

tar -acvf wicked-waifus-win-patch-win64.zip -C build .