# Xpdf output-origin source package

This package patches the exact official Xpdf4.06 source archive, SHA256
`1c38f527c46caee0f712386d42a885b96a31ed9ce11904e872559859894d137e`.
It adds a typed raw origin recorder for the separately reviewed
`pdf-text-xpdf-origin/2` profile. It preserves the reading-order text algorithm and
carries actual decoder item/scalar references through character, word and line
storage. The output stream remains converted text; it is not raw PDF byte-copy or
publisher authentication.

The raw protocol and schema are in EVENT-PROTOCOL.md and event.schema.json. The
`golden/` records are explicitly constructed consistency fixtures, without a
converter or actual authority. The standalone TEST_ONLY recorder source exercises
the same recorder module with public scalar/code literals; it does not link Xpdf
or parse PDFs. Its bounded runner is an explicit test entry point, not part of
production extraction or CI. Nothing in this package automatically runs a
converter, installs dependencies, acquires metadata or enables the profile.

`prepare_source.py RETAINED_OFFICIAL_ARCHIVE NEW_OWNED_DIRECTORY` verifies the exact
archive and authored source package, extracts into an exclusive destination,
applies only the reviewed patch and checks resulting source bytes. It performs no
network fetch, build or converter invocation. SOURCE-PINS.json binds the patch,
authored recorder, retained upstream notices and six changed/new production
source paths. Upstream is not otherwise vendored into this repository.

Build identity requires exact upstream+patch+compiler/linker/configuration and the
actual binary bytes. See BUILD-RECIPE.md. The current demonstrated build is macOS
arm64 build-only; it is not a Linux binary, native converter run, actual dependency
observation or FD3 permission. The separate native observer still denies this
channel until a reviewed policy/staging revision. Current metadata
`pdf-text-xpdf/1` quotation holds, nine-key standard receipt and public schemas are
unchanged. Future host envelopes/private observation/custody pins are required;
public raw records and successful builds cannot enroll themselves.

Upstream license/copyright notices are retained under upstream-notices/. The
upstream README describes GPLv2/GPLv3 choices; these source records are not a legal
opinion about a proposed distribution.
