import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { test } from 'node:test';
import { createBootCache, DB_PATH } from '../resources/wordpress_preview/boot-cache.mjs';

async function withCache(callback) {
    const root = await mkdtemp(join(tmpdir(), 'regexpad-boot-cache-'));
    try {
        for (const name of ['wordpress.zip', 'sqlite.zip', 'package-lock.json']) await writeFile(join(root, name), name);
        await callback(root, join(root, 'cache'));
    } finally {
        assert.equal(dirname(resolve(root)), resolve(tmpdir()));
        assert.ok(resolve(root).startsWith(join(resolve(tmpdir()), 'regexpad-boot-cache-')));
        await rm(root, { recursive: true, force: true });
    }
}

const database = Buffer.from('SQLite format 3\0demo initial database');
const fresh = { fileExists: () => true, readFileAsBuffer: () => database };

test('bootstrap database restores through the supported hook without touching core', async () => {
    await withCache(async (root, folder) => {
        const first = await createBootCache(root, folder);
        const writes = [];
        const php = { mkdir() {}, writeFile(path, bytes) { writes.push([path, bytes]); } };
        await first.restore(php);
        assert.equal(first.restored, false);
        await first.save(fresh);
        const second = await createBootCache(root, folder);
        await second.restore(php);
        assert.equal(second.restored, true);
        assert.equal(writes.length, 1);
        assert.equal(writes[0][0], DB_PATH);
        assert.deepEqual(writes[0][1], database);
    });
});

test('corrupt cache and changed runtime rebuild instead of restoring stale data', async () => {
    await withCache(async (root, folder) => {
        await (await createBootCache(root, folder)).save(fresh);
        const path = join(folder, (await readdir(folder))[0]);
        const saved = JSON.parse(await readFile(path, 'utf8'));
        saved.database = Buffer.from('corrupt').toString('base64');
        await writeFile(path, JSON.stringify(saved));
        const corrupt = await createBootCache(root, folder);
        const php = { mkdir() { assert.fail('must not restore corrupt data'); } };
        await corrupt.restore(php);
        assert.equal(corrupt.restored, false);
        await corrupt.save(fresh);
        await writeFile(join(root, 'wordpress.zip'), 'updated runtime');
        const changed = await createBootCache(root, folder);
        await changed.restore(php);
        assert.equal(changed.restored, false);
        await changed.save(fresh);
        assert.equal((await readdir(folder)).length, 2);
    });
});
