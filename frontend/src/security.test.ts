import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { describe, expect, it } from 'vitest';

// Guards the frontend's security boundary by scanning the source.

const SRC = new URL('.', import.meta.url).pathname;

function sourceFiles(dir: string): string[] {
  return readdirSync(dir).flatMap(name => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return sourceFiles(p);
    return /\.tsx?$/.test(name) && !/\.test\.tsx?$/.test(name) ? [p] : [];
  });
}

const files = sourceFiles(SRC).map(p => ({ path: relative(SRC, p), text: readFileSync(p, 'utf8') }));

describe('frontend security boundary', () => {
  it('ships no game data: test fixtures are only imported by tests', () => {
    const offenders = files.filter(f => f.text.includes('__fixtures__'));
    expect(offenders.map(f => f.path)).toEqual([]);
  });

  it('never reads or stores the join token or seat cookie in JavaScript', () => {
    const offenders = files.filter(f => /localStorage|sessionStorage|indexedDB|document\.cookie/.test(f.text));
    expect(offenders.map(f => f.path)).toEqual([]);
  });

  it('removes the join token from the address bar before using it', () => {
    const join = files.find(f => f.path === 'pages/JoinPage.tsx')!;
    const read = join.text.indexOf('window.location.hash');
    const scrub = join.text.indexOf('history.replaceState');
    const send = join.text.indexOf('api.join(');
    expect(read).toBeGreaterThan(-1);
    expect(scrub).toBeGreaterThan(read);
    expect(send).toBeGreaterThan(scrub);
  });

  it('talks only to its own origin', () => {
    const offenders = files.filter(f => /fetch\(\s*['"`]https?:|new WebSocket\(\s*['"`]wss?:/.test(f.text));
    expect(offenders.map(f => f.path)).toEqual([]);
  });

  it('uses dangerouslySetInnerHTML only for the static SVG defs', () => {
    const users = files.filter(f => f.text.includes('dangerouslySetInnerHTML')).map(f => f.path);
    expect(users).toEqual(['board/SvgDefs.tsx']);
  });

  it('does not use eval-like APIs', () => {
    const offenders = files.filter(f => /\beval\(|new Function\(|\.innerHTML\s*=/.test(f.text));
    expect(offenders.map(f => f.path)).toEqual([]);
  });
});
