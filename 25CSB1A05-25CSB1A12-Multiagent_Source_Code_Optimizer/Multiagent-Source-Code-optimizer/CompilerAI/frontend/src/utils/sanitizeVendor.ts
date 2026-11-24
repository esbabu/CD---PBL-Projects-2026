/**
 * sanitizeVendor.ts
 *
 * Ensures no external AI vendor names ("groq", "openai", "open ai")
 * are exposed in the user interface.
 */

export function sanitizeVendor(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .replace(/\bopenai\/([a-zA-Z0-9_.-]+)\b/gi, '$1')
    .replace(/\bopenai\b/gi, 'AI')
    .replace(/\bopen\s+ai\b/gi, 'AI')
    .replace(/\bgroq\b/gi, 'Optimization Engine');
}
