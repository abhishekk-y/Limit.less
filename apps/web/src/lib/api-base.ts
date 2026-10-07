// NEXT_PUBLIC_API_URL is an origin, not a versioned endpoint.
export const API_BASE = `${(process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '')}/api/v1`;
