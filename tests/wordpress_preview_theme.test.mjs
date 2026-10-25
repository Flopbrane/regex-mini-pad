import assert from 'node:assert/strict';
import { cp, mkdtemp, readFile, rm, unlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { test } from 'node:test';
import { pathToFileURL } from 'node:url';
import { installNeutralTheme, NEUTRAL_THEME, THEME_FILES } from '../resources/wordpress_preview/theme.mjs';

function memoryPhp() {
    return {
        directories: [], files: new Map(),
        mkdir(path) { this.directories.push(path); },
        writeFile(path, bytes) { this.files.set(path, bytes.toString()); },
    };
}

test('theme installer writes only the new theme inside disposable WordPress', async () => {
    const php = memoryPhp();
    await installNeutralTheme(php);
    const prefix = `/wordpress/wp-content/themes/${NEUTRAL_THEME}/`;
    assert.deepEqual([...php.files.keys()], THEME_FILES.map((name) => prefix + name));
    assert.deepEqual(php.directories, [prefix + 'templates']);
    assert.match(php.files.get(prefix + 'style.css'), /Theme Name: RegexPad Neutral Preview/);
    const theme = JSON.parse(php.files.get(prefix + 'theme.json'));
    assert.equal(theme.version, 3);
    assert.deepEqual(theme.settings, { layout: { contentSize: '100%', wideSize: '100%' } });
    assert.deepEqual(theme.styles, { spacing: { blockGap: '0' } });
    assert.equal(php.files.get(prefix + 'templates/index.html').trim(),
        '<!-- wp:post-content {"layout":{"type":"default"}} /-->');
});

test('theme assets resolve after copying resources into a packaged layout', async () => {
    const temporary = await mkdtemp(join(tmpdir(), 'regexpad-preview-theme-'));
    try {
        const destination = join(temporary, '_internal', 'resources', 'wordpress_preview');
        await cp(new URL('../resources/wordpress_preview/', import.meta.url), destination, { recursive: true });
        const installed = await import(pathToFileURL(join(destination, 'theme.mjs')).href);
        const php = memoryPhp();
        await installed.installNeutralTheme(php);
        assert.equal(php.files.size, 3);
        const bridge = await readFile(join(destination, 'bridge.mjs'), 'utf8');
        assert.match(bridge, /from '\.\/theme\.mjs'/);
        await unlink(join(destination, 'themes', NEUTRAL_THEME, 'theme.json'));
        const incomplete = memoryPhp();
        await assert.rejects(installed.installNeutralTheme(incomplete), { code: 'ENOENT' });
        assert.equal(incomplete.files.size, 0);
        assert.equal(incomplete.directories.length, 0);
    } finally {
        const target = resolve(temporary);
        assert.equal(dirname(target), resolve(tmpdir()));
        assert.ok(target.startsWith(join(resolve(tmpdir()), 'regexpad-preview-theme-')));
        await rm(target, { recursive: true, force: true });
    }
});
