import  { createServerEntry } from '@tanstack/react-start/server-entry';
import { createStartHandler, defaultStreamHandler, defineHandlerCallback } from '@tanstack/react-start/server';
import { logger } from '@lib/logger';

const customHandler = defineHandlerCallback((ctx) => {
  // Log incoming request
  const { pathname, search } = new URL(ctx.request.url);
  logger.debug({ method: ctx.request.method, path: pathname, query: search }, 'Incoming request');

  // Call default stream handler
  return defaultStreamHandler(ctx);
});

const fetch = createStartHandler(customHandler);

export default createServerEntry({
  fetch,
});