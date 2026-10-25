# RegexPad source code and release correspondence

**Application license: GPL-3.0-only**  
Documentation updated: 2026-10-25

[Public source repository](https://github.com/Flopbrane/regex-mini-pad) ·
[GPLv3 text](LICENSE) · [License notice](LICENSE.txt) ·
[Third-party notices](THIRD_PARTY_NOTICES.md)

## Application source

RegexPad's original application code is provided under GNU GPL version 3 only.
The public repository above is the source entry point. Public visibility alone
does not grant GPL rights; the license declaration and the full [LICENSE](LICENSE)
supply the project terms for the code they cover. Separate third-party notices
remain in force.

Source is not limited to an arbitrary latest main branch. A distributed binary
must point to the revision from which it was actually built.

| Item | Release policy / current status |
|---|---|
| Application version | 1.0.0 |
| SPDX identifier | GPL-3.0-only |
| Intended release tag | `v1.0.0`; planned, not created or published by this documentation task |
| Actual binary source commit | Record at build/release time; not assigned to an older EXE by this document |
| Binary/source publication | Separate release work; this task changes local documents only |

## Producing a matching release

1. Commit all intended application code, resources, dictionaries, build scripts,
   requirements, license texts and notices. Include any changes needed to build
   the executable; retain separate rights on third-party materials.
2. Identify a clean source revision and create/publish the version tag for that
   revision. Build the EXE from that exact revision, not later uncommitted edits.
3. With the binary download, provide the exact repository revision/tag and the
   corresponding source archive. Include the instructions/scripts needed to
   generate, install and run the executable as required by the applicable GPL
   source provisions. Do not rely on a moving main branch as version proof.
4. Record the commit, tag, build environment, dependency/runtime versions and
   binary/source archive SHA-256 values in the release information. Check a fresh
   extraction of the distributed folder before archiving it.
5. Preserve the application GPL text and all applicable dependency/copyright
   notices. Keep source access available as required by the distribution method
   actually used. This file is not a substitute for fulfilling those duties.

For source/build entry points, see [README](README.md),
[the user guide's packaging section](docs/HOW_TO_USE.md#development-and-packaging),
`requirements_dev.txt`, `regex-pad.spec`, and `build.ps1`.
The maintained environment uses Python 3.12. On another build PC, provide the
corresponding environment and adjust the local Python path in `build.ps1`;
the hard-coded developer path is not an extra license restriction.

## Dependency source is separate

RegexPad's GitHub repository does not by itself contain the complete matching
source of PySide6, Shiboken6, Qt, or every bundled runtime. Preserve the original
license/copyright notices and identify the actual dependency versions, build
configuration and changes, if any.

The [Qt source references](LICENSES/qt-for-python/SOURCES.md) and
[Virtual Keyboard third-party notices](LICENSES/qt-virtual-keyboard/SOURCES.md)
are reference/provenance lists, not a declaration that every binary has already
been matched to a complete source-delivery package. A distributor must supply
or provide access to Corresponding Source in a manner allowed by the applicable
license and actual distribution arrangement. No owner-specific written source
offer is invented here.

## 日本語

RegexPad本体の独自コードはGPL-3.0-onlyで提供します。公開GitHubへの入口はページ上部です。
「Publicで閲覧できること」と「GPLでの利用・改変・再配布を許諾すること」は区別し、
許諾はLICENSEと本体のライセンス通知に明示しています。

EXE配布時には、実際にビルドしたコミットとタグを記録し、対応するソース・ビルド手順へ
たどれるようにします。`v1.0.0`は予定するタグ名で、今回作成・公開したものではありません。
既存EXEに後からそのタグ名だけを付けて、対応済みと扱うこともしません。

ライセンス関連文書とソース変更を確定・コミットし、その版をタグ付けしてビルドしたうえで、
バイナリーと対応ソースを配布する手順です。未コミットの変更から作ったEXEを、
別のタグのソースと対応させないでください。

Qt・PySide等の対応ソースはRegexPadのソースとは別に確認が必要です。
上流URLや原文の同梱だけで、必要な提供をすべて完了したとは記載しません。
今回の作業はローカル文書の更新であり、GitHubへのpush、タグ作成、EXE再ビルド、
ZIP・Releaseの公開は含めていません。
