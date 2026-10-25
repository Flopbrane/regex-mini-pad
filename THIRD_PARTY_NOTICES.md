# RegexPad: third-party notices and GPLv3 distribution policy

Updated: 2026-10-25. Documentation baseline: RegexPad 1.0.0.

## RegexPad license and public source

RegexPad's original application code is distributed under **GNU GPL version 3
only (`GPL-3.0-only`)**. The previous office/internal-use restriction has been
replaced for that code. See [LICENSE](LICENSE), [LICENSE.txt](LICENSE.txt), and
[the source/release guide](SOURCE_CODE.md).

Public source: [Flopbrane/regex-mini-pad](https://github.com/Flopbrane/regex-mini-pad).

Use, modification and redistribution, including distribution for a fee, are
permitted under the GPL's terms. A Public repository alone is not a GPL
declaration, nor proof that an EXE matches the latest branch. An actual release
must identify its built source revision and fulfill applicable source-delivery
and notice duties. The proposed `v1.0.0` tag is not represented as published by
this local documentation task.

Third-party components and materials keep their respective copyright and
license notices. The project's GPL declaration does not replace permissive
notices or unilaterally relicense dependency source. This is a targeted Qt
notice, not a complete inventory of all bundled components.

## Qt for Python, Shiboken6 and Qt

The configured environment reports version **6.11.2** for PySide6,
PySide6_Essentials, PySide6_Addons and shiboken6. Installed metadata states
`LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`. The project uses the GPLv3
open-source route for the relevant Qt/PySide components; it does not claim to
hold a commercial Qt contract. Check each actual module/file and dependency
rather than applying the top-level metadata to every library.

Qt and Qt for Python are copyright The Qt Company and other contributors.
Retain upstream copyright notices. Official references:
[Qt for Python](https://doc.qt.io/qtforpython-6.11/),
[Qt 6.11 licensing](https://doc.qt.io/qt-6.11/licensing.html),
[Qt for Python third-party code](https://doc.qt.io/qtforpython-6.11/licenses.html),
and [Qt third-party code](https://doc.qt.io/qt-6.11/licenses-used-in-qt.html).

Original texts/provenance are under [LICENSES/qt-for-python/](LICENSES/qt-for-python/SOURCES.md):
[GPLv3](LICENSES/qt-for-python/GPL-3.0-only.txt),
[LGPLv3](LICENSES/qt-for-python/LGPL-3.0-only.txt), and
[GPLv2](LICENSES/qt-for-python/GPL-2.0-only.txt).
The [commercial reference](LICENSES/qt-for-python/LicenseRef-Qt-Commercial.txt)
is preserved as an upstream notice; including it grants no commercial rights.
Original license texts are unchanged.

## Qt Virtual Keyboard and its third-party notices

The existing distribution includes `_internal/PySide6/Qt6VirtualKeyboard.dll`
and `plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll`. The
[official Qt 6.11 module page](https://doc.qt.io/qt-6.11/qtvirtualkeyboard-index.html)
lists **GPLv3 or commercial**, not LGPLv3. Under this project's declared
open-source policy, the applicable GPLv3 terms and notices must accompany that
component. GPLv3's availability does not remove its source/copyright duties.

Qt documents these optional third-party input engines. Their original notices
from Qt's v6.11.2 source tree are included unchanged; this does not claim each
engine is enabled in every shipped binary.

| Component | Upstream license declaration | Included original notice |
|---|---|---|
| OpenWnn | Apache-2.0 | [OpenWnn NOTICE](LICENSES/qt-virtual-keyboard/OpenWnn-NOTICE.txt) |
| PinyinIME | Apache-2.0 | [PinyinIME NOTICE](LICENSES/qt-virtual-keyboard/PinyinIME-NOTICE.txt) |
| Traditional Chinese IME (tcime) | Apache-2.0 AND BSD-3-Clause | [TCIME COPYING](LICENSES/qt-virtual-keyboard/TCIME-COPYING.txt) |

Keep the copyright names, license terms and any included notices in those
original files. The [provenance record](LICENSES/qt-virtual-keyboard/SOURCES.md)
links to source paths and hashes. Check the actual build for additional
dependencies/notices; inclusion of these three files is not an exhaustive audit.

The local application source contains no explicit Virtual Keyboard use found
in this inspection. PyInstaller's QtGui hook collects the
`platforminputcontexts` plugin family; its collection records contain this
plugin and DLL. This explains their inclusion without proving they are
required or safe to remove. No DLL/plugin has been removed in this task.

## Other observed Qt modules

The existing distribution also contains Core, Gui, Network, OpenGL, Widgets,
Svg, Qml, QmlMeta, QmlModels, QmlWorkerScript, Quick and Pdf DLLs. These are
separate files under `_internal/PySide6/`, with Shiboken under
`_internal/shiboken6/`. An installed package version is not complete
provenance for an old frozen executable.

[Qt PDF 6.11](https://doc.qt.io/qt-6.11/qtpdf-index.html) has
LGPLv3/GPLv2/commercial alternatives and embedded third-party code such as
PDFium. Such dependencies retain their own terms and notices. This document
does not claim every transitive component or its matching source is accounted
for. Python, WordPress, Node, PHP.wasm and SQLite integration also retain their
own applicable notices.

## Release correspondence and remaining work

The [source/release guide](SOURCE_CODE.md) defines the intended matching-binary
process. Before an actual release:

1. Commit/publish the GPL declaration and all source/build inputs, then build
   from the exact release revision and record its commit/tag with the download.
2. Provide the applicable Corresponding Source, including required build and
   installation information, for RegexPad and relevant dependency binaries.
   A link to a moving application branch is not a substitute for matching
   dependency source.
3. Keep recipients' GPL rights and any separately applicable LGPL rights
   intact. Do not impose office-only, noncommercial, or blanket
   no-modification/no-reverse-engineering restrictions.
4. Match Qt modules and enabled third-party components to their original
   copyright/license notices; retain them in binary and source distributions
   as required by their actual licenses.

This local documentation change has not pushed GitHub changes, created a
release tag, rebuilt EXEs/ZIPs, delivered a complete dependency source set, or
tested modified-library replacement on a frozen EXE. Those are recorded as
release work, not completed merely by writing these notices.

## 日本語

RegexPad本体の独自コードをGPL-3.0-onlyとし、従来の社内・内部利用限定の条件を置き換えました。
GPLの条件に従い、利用・改変・再配布ができ、有償での配布も可能です。
公開GitHubへのリンクと全文のLICENSEを用意し、別条件の第三者部品・資料の表示は維持します。

Qt Virtual KeyboardはGPLv3または商用条件です。今回はGPLv3のオープンソース経路で整理し、
商用契約を取得済みとは記載していません。OpenWnn、PinyinIME、tcimeの上流原文も同梱します。
それぞれが実際のバイナリーで有効か、他の帰属表示が必要かは、最終ビルドで照合します。
本体をGPLにすることだけで、第三者部品の条件が消えるわけではありません。

公開ソースがあることと、配布するEXEに対応する完全なソースが提供されていることは別です。
必要なビルド情報やQt側の対応ソースも確認し、実際の版をタグ・コミットで特定します。
`v1.0.0`は予定名で、作成・公開済み、既存EXEと対応済みとは記載しません。

今回行ったのはライセンス関係文書の更新と同梱です。
GitHubへのpush、タグ作成、不要DLLの除外、EXE・ZIP・Releaseの再作成は行っていません。
