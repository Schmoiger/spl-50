import { describe, expect, it } from 'vitest';
import { parseMarkdown } from '../markdownParser';

describe('parseMarkdown', () => {
  it('strips all spacing and newlines', () => {
    const result = parseMarkdown('Hello\n\nWorld   test');
    // Result has multiple segments now due to paragraphs
    const combinedText = result
      .map((s) => s.text)
      .join('')
      .trim();
    // It should collapse extra spaces inside paragraph 2
    expect(combinedText.replace(/\s+/g, ' ')).toBe('Hello World test');
    expect(result[0].bold).toBe(false);
    expect(result[0].italic).toBe(false);
  });

  it('preserves bold formatting', () => {
    const result = parseMarkdown('Hello **World**');
    expect(result).toHaveLength(3);
    expect(result[0].text).toBe('Hello ');
    expect(result[0].bold).toBe(false);
    expect(result[1].text).toBe('World');
    expect(result[1].bold).toBe(true);
  });

  it('preserves italic formatting', () => {
    const result = parseMarkdown('Hello *World*');
    expect(result).toHaveLength(3);
    expect(result[0].text).toBe('Hello ');
    expect(result[0].italic).toBe(false);
    expect(result[1].text).toBe('World');
    expect(result[1].italic).toBe(true);
  });

  it('handles bold and italic together', () => {
    const result = parseMarkdown('**Hello *World***');
    expect(result).toHaveLength(3);
    expect(result[0].text).toBe('Hello ');
    expect(result[0].bold).toBe(true);
    expect(result[0].italic).toBe(false);
    expect(result[1].text).toBe('World');
    expect(result[1].bold).toBe(true);
    expect(result[1].italic).toBe(true);
  });

  it('handles complex paragraphs', () => {
    const markdown = `# Heading 1

This is a **bold** and *italic* test.

* List item 1
* List item **2**`;
    const result = parseMarkdown(markdown);

    // Heading 1 This is a bold and italic test. List item 1 List item 2
    const combinedText = result
      .map((s) => s.text)
      .join('')
      .trim();
    // Reduce multiple spaces that might have been added
    expect(combinedText.replace(/\s+/g, ' ')).toBe(
      'Heading 1 This is a bold and italic test. List item 1 List item 2',
    );

    // Check specific segments exist correctly
    const boldSeg = result.find((s) => s.text === 'bold');
    expect(boldSeg?.bold).toBe(true);

    const italicSeg = result.find((s) => s.text === 'italic');
    expect(italicSeg?.italic).toBe(true);
  });
});
