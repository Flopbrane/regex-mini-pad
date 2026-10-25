// Cache only the freshly installed demo database, before any editor text is sent.
import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

export const DB_PATH = '/wordpress/wp-content/database/.ht.sqlite';
const digest = (data) => createHash('sha256').update(data).digest('hex');

export async function createBootCache(root, cacheRoot) {
    const key = createHash('sha256').update('regexpad-demo-db-v1');
    for (const name of ['wordpress.zip', 'sqlite.zip', 'package-lock.json']) key.update(await readFile(join(root, name)));
    const path = join(cacheRoot, `bootstrap-${key.digest('hex')}.json`);
    let restored = false;
    return {
        get restored() { return restored; },
        async restore(php) {
            try {
                const saved = JSON.parse(await readFile(path, 'utf8'));
                const bytes = Buffer.from(saved.database, 'base64');
                if (saved.sha256 !== digest(bytes) || bytes.subarray(0, 16).toString() !== 'SQLite format 3\0') return;
                await php.mkdir('/wordpress/wp-content/database');
                await php.writeFile(DB_PATH, bytes);
                restored = true;
            } catch (error) {
                // A missing/interrupted/corrupt cache falls back to a fresh install.
                if (error.code !== 'ENOENT' && !(error instanceof SyntaxError) && !(error instanceof TypeError)) throw error;
            }
        },
        async save(php) {
            if (restored || !await php.fileExists(DB_PATH)) return;
            const bytes = Buffer.from(await php.readFileAsBuffer(DB_PATH));
            if (bytes.subarray(0, 16).toString() !== 'SQLite format 3\0') return;
            await mkdir(cacheRoot, { recursive: true });
            const temporary = `${path}.${randomUUID()}.tmp`;
            await writeFile(temporary, JSON.stringify({ sha256: digest(bytes), database: bytes.toString('base64') }));
            await rename(temporary, path);
        },
    };
}
