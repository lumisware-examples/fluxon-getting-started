import type { NextConfig } from 'next';

const config: NextConfig = {
  distDir: process.env.NEXT_DIST_DIR || '.next',
  poweredByHeader: false,
  experimental: process.env.NODE_ENV === 'production' ? { cssChunking: 'strict' } : { reactDebugChannel: false },
};

export default config;
