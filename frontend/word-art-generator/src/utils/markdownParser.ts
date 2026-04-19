import { lexer } from 'marked';
import type { Token, Tokens } from 'marked';

export interface TextSegment {
  text: string;
  bold: boolean;
  italic: boolean;
  paragraphIndex: number;
}

export function parseMarkdown(markdown: string): TextSegment[] {
  const tokens = lexer(markdown);
  const segments: TextSegment[] = [];
  let currentParagraphIndex = 0;

  function walk(tokens: Token[], bold = false, italic = false) {
    for (const token of tokens) {
      if (token.type === 'strong') {
        walk((token as Tokens.Strong).tokens || [], true, italic);
      } else if (token.type === 'em') {
        walk((token as Tokens.Em).tokens || [], bold, true);
      } else if (token.type === 'text') {
        const t = token as Tokens.Text;
        if (t.tokens && t.tokens.length > 0) {
          walk(t.tokens, bold, italic);
        } else {
          // Collapse whitespace (spaces, newlines, tabs) into a single space
          const cleanText = t.text.replace(/\s+/g, ' ');
          if (cleanText) {
            segments.push({ text: cleanText, bold, italic, paragraphIndex: currentParagraphIndex });
          }
        }
      } else if (token.type === 'paragraph' || token.type === 'heading') {
        const t = token as (Tokens.Paragraph | Tokens.Heading);
        walk(t.tokens || [], bold, italic);
        segments.push({ text: ' ', bold: false, italic: false, paragraphIndex: currentParagraphIndex });
        currentParagraphIndex++;
      } else if (token.type === 'list') {
        walk((token as Tokens.List).items || [], bold, italic);
      } else if (token.type === 'list_item') {
        walk((token as Tokens.ListItem).tokens || [], bold, italic);
        segments.push({ text: ' ', bold: false, italic: false, paragraphIndex: currentParagraphIndex });
        currentParagraphIndex++;
      } else if ((token as any).tokens) {
        walk((token as any).tokens, bold, italic);
      }
    }
  }

  walk(tokens);
  
  // Condense adjacent segments with the same formatting
  const condensed: TextSegment[] = [];
  for (const seg of segments) {
    const last = condensed[condensed.length - 1];
    if (last && last.bold === seg.bold && last.italic === seg.italic && last.paragraphIndex === seg.paragraphIndex) {
      last.text += seg.text;
    } else {
      condensed.push({ ...seg });
    }
  }
  
  return condensed;
}
