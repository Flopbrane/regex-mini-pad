// Runs official WordPress/PHP.wasm in memory. No PHP is evaluated from editor text.
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { createRequire } from 'node:module';
import { join, resolve } from 'node:path';
import { createInterface } from 'node:readline';
import { pathToFileURL } from 'node:url';

const root = resolve(process.argv[2]);
const require = createRequire(join(root, 'package.json'));
const load = (name) => import(pathToFileURL(require.resolve(name).replace(/\.cjs$/, '.js')).href);
const { bootWordPressAndRequestHandler } = await load('@wp-playground/wordpress');
const { loadPHPRuntime } = await load('@php-wasm/universal');
const { getPHPLoaderModule } = await load('@php-wasm/node-8-3');
const send = (data) => process.stdout.write(`REGEXPAD_PREVIEW ${JSON.stringify(data)}\n`);
let handler;
let queue = Promise.resolve();
let closing = false;
const enqueue = (callback) => {
    const result = queue.then(callback);
    queue = result.catch(() => {});
    return result;
};

// The HTTP listener is always loopback-only. Updates arrive through private stdin,
// never through a website, query string, or unauthenticated HTTP write endpoint.
const server = createServer((request, response) => {
    if (!handler) { response.writeHead(503); response.end('WordPress is starting.'); return; }
    if (!['GET', 'HEAD'].includes(request.method)) {
        response.writeHead(405); response.end(); return;
    }
    if (request.headers.host !== `127.0.0.1:${server.address().port}`) {
        response.writeHead(403); response.end(); return;
    }
    enqueue(async () => {
        const result = await handler.request({
            url: request.url, method: request.method,
            headers: Object.fromEntries(Object.entries(request.headers).map(([key, value]) => [key, Array.isArray(value) ? value.join(', ') : value ?? ''])),
        });
        response.writeHead(result.httpStatusCode, { ...result.headers, 'cache-control': 'no-store' });
        response.end(request.method === 'HEAD' ? undefined : result.bytes);
    }).catch((error) => {
        console.error(error);
        if (!response.headersSent) response.writeHead(500);
        response.end('WordPress preview failed.');
    });
});

async function stop() {
    if (closing) return;
    closing = true;
    server.closeAllConnections();
    await new Promise((done) => server.close(done));
    await queue;
    if (handler) await handler[Symbol.asyncDispose]();
}

try {
    await new Promise((done, reject) => {
        server.once('error', reject);
        server.listen(0, '127.0.0.1', done);
    });
    const siteUrl = `http://127.0.0.1:${server.address().port}`;
    send({ event: 'progress', stage: 'boot' });
    handler = await bootWordPressAndRequestHandler({
        siteUrl, documentRoot: '/wordpress', maxPhpInstances: 1,
        createPhpRuntime: async () => loadPHPRuntime(await getPHPLoaderModule()),
        phpVersion: '8.3', cookieStore: false,
        wordPressZip: new File([await readFile(join(root, 'wordpress.zip'))], 'wordpress.zip'),
        sqliteIntegrationPluginZip: new File([await readFile(join(root, 'sqlite.zip'))], 'sqlite.zip'),
        constants: {
            WP_ENVIRONMENT_TYPE: 'local', WP_HTTP_BLOCK_EXTERNAL: true,
            AUTOMATIC_UPDATER_DISABLED: true, DISABLE_WP_CRON: true,
        },
    });
    const php = await handler.getPrimaryPhp();
    const info = await php.run({ code: `<?php require '/wordpress/wp-load.php';
        update_option('blogname', 'RegexPad WordPress Preview');
        update_option('blogdescription', 'normal / local preview');
        update_option('blog_public', 0);
        echo json_encode(['version' => get_bloginfo('version'), 'theme' => get_stylesheet()]);` });
    if (info.exitCode !== 0) throw new Error(info.errors || 'WordPress initialization failed');
    send({ event: 'ready', ...JSON.parse(info.text), origin: siteUrl });

    for await (const line of createInterface({ input: process.stdin, crlfDelay: Infinity })) {
        const command = JSON.parse(line);
        if (command.command === 'shutdown') break;
        if (command.command !== 'render') continue;
        try {
            await enqueue(async () => {
                const payload = Buffer.from(JSON.stringify({ title: command.title, content: command.content })).toString('base64');
                // Base64 contains no PHP quoting characters. User source is always data.
                const result = await php.run({ code: `<?php require '/wordpress/wp-load.php';
                    wp_set_current_user(1);
                    $data = json_decode(base64_decode('${payload}'), true);
                    $post = [
                        'post_title' => $data['title'], 'post_content' => $data['content'],
                        'post_status' => 'publish', 'post_type' => 'post',
                        'comment_status' => 'closed', 'ping_status' => 'closed',
                    ];
                    $existing = (int) get_option('regexpad_preview_post', 0);
                    if ($existing) $post['ID'] = $existing;
                    $id = wp_insert_post(wp_slash($post), true);
                    if (is_wp_error($id)) { echo json_encode(['error' => $id->get_error_message()]); exit; }
                    update_option('regexpad_preview_post', $id);
                    echo json_encode(['url' => get_permalink($id)]);` });
                if (result.exitCode !== 0) throw new Error(result.errors || 'WordPress rendering failed');
                const rendered = JSON.parse(result.text);
                if (rendered.error) throw new Error(rendered.error);
                const url = new URL(rendered.url);
                if (url.origin !== siteUrl) throw new Error('Unexpected preview origin');
                url.searchParams.set('regexpad_revision', String(command.id));
                // Exercise the real front-end request, including dynamic blocks
                // and the standard theme. Rendering success is not HTML validity.
                const page = await handler.request({ url: url.pathname + url.search });
                send({ event: 'feedback', id: command.id, status: page.httpStatusCode, warnings: page.errors });
                if (page.httpStatusCode >= 400) throw new Error(page.errors || `WordPress HTTP ${page.httpStatusCode}`);
                send({ event: 'rendered', id: command.id, url: url.href });
            });
        } catch (error) {
            send({ event: 'error', id: command.id, message: String(error.message ?? error) });
        }
    }
    await stop();
} catch (error) {
    send({ event: 'error', message: String(error.message ?? error) });
    await stop().catch(() => {});
    process.exitCode = 1;
}
