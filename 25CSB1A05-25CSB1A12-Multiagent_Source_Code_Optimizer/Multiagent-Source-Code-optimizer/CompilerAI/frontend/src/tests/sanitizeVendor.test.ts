import { describe, it } from 'node:test';
import assert from 'node:assert';
import { sanitizeVendor } from '../utils/sanitizeVendor';

describe('sanitizeVendor utility', () => {
  it('strips "openai/" model prefixes', () => {
    assert.strictEqual(sanitizeVendor('openai/gpt-oss-120b'), 'gpt-oss-120b');
    assert.strictEqual(sanitizeVendor('Model is openai/gpt-oss-120b.'), 'Model is gpt-oss-120b.');
  });

  it('replaces "groq" and "Groq" with vendor-neutral terms', () => {
    assert.strictEqual(sanitizeVendor('Connected to Groq API'), 'Connected to Optimization Engine API');
    assert.strictEqual(sanitizeVendor('groq model response received'), 'Optimization Engine model response received');
    assert.strictEqual(sanitizeVendor('Optimization Agent initialized with Groq Algo Agent'), 'Optimization Agent initialized with Optimization Engine Algo Agent');
  });

  it('replaces "openai" and "open ai" variants', () => {
    assert.strictEqual(sanitizeVendor('Using OpenAI service'), 'Using AI service');
    assert.strictEqual(sanitizeVendor('Powered by Open AI'), 'Powered by AI');
    assert.strictEqual(sanitizeVendor('openai embeddings'), 'AI embeddings');
  });

  it('preserves clean text without vendor references', () => {
    const text = 'Line 14: Replaced nested loop with two-pointer technique';
    assert.strictEqual(sanitizeVendor(text), text);
  });

  it('handles null and undefined safely', () => {
    assert.strictEqual(sanitizeVendor(null), '');
    assert.strictEqual(sanitizeVendor(undefined), '');
  });
});
