# Explicit build-only recipe

No command below invokes the resulting converter, even for a version/help query.
Source preparation is safe to test separately. Build tools must already exist; no
dependency installation is part of this recipe. Keep all outputs in new owned
directories and retain the exact commands, actual exits, logs and content hashes.
Do not reuse a predecessor extraction workspace.

1. Obtain and independently retain the official source archive from
   https://dl.xpdfreader.com/xpdf-4.06.tar.gz. Check its exact pinned SHA256 in
   SOURCE-PINS.json; no alternate release or mirror is silently selected.
2. Use the source preparer with explicit retained archive and new owned paths:

   ```sh
   python3 bench/pinned-candidate/xpdf-origin/prepare_source.py "$RETAINED_ARCHIVE" "$NEW_SOURCE_DIRECTORY"
   ```

3. Configure the prepared xpdf-4.06 directory with existing C/C++ compiler and CMake
   paths, an out-of-source owned build directory, Release, disabled Qt/PNG GUI
   discovery, MULTITHREADED=OFF and NO_FONTCONFIG=ON. The demonstrated macOS build
   used these exact flags:

   ```text
   -DCMAKE_BUILD_TYPE=Release
   -DCMAKE_DISABLE_FIND_PACKAGE_Qt6Widgets=TRUE
   -DCMAKE_DISABLE_FIND_PACKAGE_Qt5Widgets=TRUE
   -DCMAKE_DISABLE_FIND_PACKAGE_PNG=TRUE
   -DMULTITHREADED=OFF
   -DNO_FONTCONFIG=ON
   -DCMAKE_C_COMPILER=/usr/bin/clang
   -DCMAKE_CXX_COMPILER=/usr/bin/clang++
   ```

4. Build only target `pdftotext`, with at most two parallel compiler jobs. Retain
   verbose compile/link argv and version output from the compiler, linker and
   CMake. Retain generated configuration/source hashes and each object/archive and
   final artifact hash. Inspecting linked-library metadata is build evidence only;
   it does not establish actual runtime reads/maps or closure.
5. For eventual output-conservation fixtures, an unpatched build must use the
   exact same source release, compiler/configuration and input/config contract.
   Such converter/PDF executions require separate authorization. Do not execute
   them during source/build checks.

The first recorded author build found the existing fontconfig library while the
upstream build omitted its installed header path; compilation failed on that
header. The failed log is retained. The generic build identity was then explicitly
selected with upstream NO_FONTCONFIG=ON, before any private document or converter
execution. The successful identity is not claimed equivalent to an installed
converter or its output. Actual Linux build/runtime fit remains unestablished.

A successful build establishes compilation/linking of this source/configuration
only. It does not establish complete native emission coverage, byte equality with
an unpatched converter, runtime access observation, host mutation control,
privately acquired actual metadata, rights/age facts, qualification or permission.
