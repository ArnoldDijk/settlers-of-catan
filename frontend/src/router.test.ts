import { describe, expect, it } from 'vitest';
import { matchRoute } from './router';

describe('matchRoute', () => {
  it('knows the pages', () => {
    expect(matchRoute('/')).toEqual({ page: 'lobby' });
    expect(matchRoute('/join')).toEqual({ page: 'join' });
    expect(matchRoute('/tegelset')).toEqual({ page: 'tiles' });
    expect(matchRoute('/games/Ab3_x-9Qz')).toEqual({ page: 'game', gameId: 'Ab3_x-9Qz' });
  });

  it('rejects malformed game ids', () => {
    expect(matchRoute('/games/../../etc')).toEqual({ page: 'notFound' });
    expect(matchRoute('/games/short')).toEqual({ page: 'notFound' });
  });
});
