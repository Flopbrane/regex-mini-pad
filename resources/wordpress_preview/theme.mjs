// These assets belong to RegexPad, not to the downloaded WordPress runtime.
import { readFile } from 'node:fs/promises';

export const NEUTRAL_THEME = 'regexpad-preview';
export const THEME_FILES = ['style.css', 'theme.json', 'templates/index.html'];

export async function installNeutralTheme(php) {
    // Resolve beside the bridge resources, including an EXE's _internal folder.
    // Load all assets before writing to the disposable PHP filesystem.
    const files = await Promise.all(THEME_FILES.map(async (name) => [
        name, await readFile(new URL(`./themes/${NEUTRAL_THEME}/${name}`, import.meta.url)),
    ]));
    const destination = `/wordpress/wp-content/themes/${NEUTRAL_THEME}`;
    php.mkdir(`${destination}/templates`);
    for (const [name, contents] of files) php.writeFile(`${destination}/${name}`, contents);
}
