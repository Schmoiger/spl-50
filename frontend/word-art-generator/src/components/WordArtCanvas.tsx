import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { parseMarkdown, type TextSegment } from '../utils/markdownParser';

interface WordArtCanvasProps {
  markdownText: string;
  calligramText: string;
  bgColor: string;
  textColor: string;
  textColor2: string;
  calligramColor: string;
}

export interface WordArtCanvasRef {
  exportToPNG: () => void;
}

const CANVAS_WIDTH = 1200;
const CANVAS_HEIGHT = 800;
const LINE_SPACING = 1.1; // Line height multiplier
const FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const CALLIGRAM_FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const BASE_COLOR = '#8e9e9a'; // Comforting grey (sea foam hint)
const CALLIGRAM_COLOR = '#7e22ce'; // Sophisticated purple

export const WordArtCanvas = forwardRef<WordArtCanvasRef, WordArtCanvasProps>(
  ({ markdownText, calligramText, bgColor, textColor, textColor2, calligramColor }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useImperativeHandle(ref, () => ({
      exportToPNG: () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = 'word-art.png';
        a.click();
      },
    }));

    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;

      // 1. Clear background
      ctx.fillStyle = bgColor || '#ffffff';
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      if (!markdownText) return;

      // 2. Parse markdown
      const segments = parseMarkdown(markdownText);
      if (segments.length === 0) return;

      // 3. Create calligram mask
      const maskCanvas = document.createElement('canvas');
      maskCanvas.width = CANVAS_WIDTH;
      maskCanvas.height = CANVAS_HEIGHT;
      const maskCtx = maskCanvas.getContext('2d', { willReadFrequently: true });
      if (maskCtx && calligramText) {
        maskCtx.fillStyle = 'black';
        maskCtx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        maskCtx.fillStyle = 'white';
        maskCtx.textAlign = 'center';
        maskCtx.textBaseline = 'middle';
        
        // Scale calligram text to fit nicely
        let cSize = 500;
        maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
        while (maskCtx.measureText(calligramText).width > CANVAS_WIDTH * 0.9 && cSize > 50) {
          cSize -= 10;
          maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
        }
        
        maskCtx.fillText(calligramText, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
      }

      // 4. Calculate font size
      // Measure total width at a base font size
      const baseSize = 100;
      let totalBaseWidth = 0;
      
      const measureCtx = document.createElement('canvas').getContext('2d')!;
      for (const seg of segments) {
        const weight = seg.bold ? 'bold' : 'normal';
        const style = seg.italic ? 'italic' : 'normal';
        measureCtx.font = `${style} ${weight} ${baseSize}px ${FONT_FAMILY}`;
        totalBaseWidth += measureCtx.measureText(seg.text).width;
      }
      
      const widthAt1px = totalBaseWidth / baseSize;
      
      // We need: (widthAt1px * fontSize / CANVAS_WIDTH) * (fontSize * LINE_SPACING) = CANVAS_HEIGHT
      // fontSize^2 = (CANVAS_WIDTH * CANVAS_HEIGHT) / (widthAt1px * LINE_SPACING)
      // Use 0.95 multiplier for safety margin
      let fontSize = Math.sqrt((CANVAS_WIDTH * CANVAS_HEIGHT) / (widthAt1px * LINE_SPACING)) * 0.95;
      
      // 5. Draw text
      let maskData: ImageData | null = null;
      if (maskCtx && calligramText) {
        maskData = maskCtx.getImageData(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
      }

      interface RenderChar {
        char: string;
        weight: string;
        style: string;
        width: number;
        paragraphIndex: number;
      }
      
      const allChars: RenderChar[] = [];
      
      for (const seg of segments) {
        const weight = seg.bold ? 'bold' : 'normal';
        const style = seg.italic ? 'italic' : 'normal';
        ctx.font = `${style} ${weight} ${fontSize}px ${FONT_FAMILY}`;
        
        for (let i = 0; i < seg.text.length; i++) {
          const char = seg.text[i];
          const width = ctx.measureText(char).width;
          allChars.push({ char, weight, style, width, paragraphIndex: seg.paragraphIndex });
        }
      }

      let currentLine: RenderChar[] = [];
      let currentLineWidth = 0;
      const lines: { chars: RenderChar[], extraSpace: number }[] = [];

      for (const charInfo of allChars) {
        if (currentLineWidth + charInfo.width > CANVAS_WIDTH && currentLine.length > 0) {
          lines.push({ chars: currentLine, extraSpace: CANVAS_WIDTH - currentLineWidth });
          currentLine = [];
          currentLineWidth = 0;
          // Skip leading space on a new line for cleaner wrapping
          if (charInfo.char === ' ') {
            continue;
          }
          currentLine.push(charInfo);
          currentLineWidth += charInfo.width;
        } else {
          currentLine.push(charInfo);
          currentLineWidth += charInfo.width;
        }
      }
      if (currentLine.length > 0) {
        // Last line is not justified
        lines.push({ chars: currentLine, extraSpace: 0 });
      }

      let y = fontSize;
      ctx.textBaseline = 'bottom';
      
      for (const line of lines) {
        if (y - fontSize > CANVAS_HEIGHT) break;
        
        let x = 0;
        const spacing = line.chars.length > 1 ? line.extraSpace / (line.chars.length - 1) : 0;
        
        for (const charInfo of line.chars) {
          ctx.font = `${charInfo.style} ${charInfo.weight} ${fontSize}px ${FONT_FAMILY}`;
          
          let color = charInfo.paragraphIndex % 2 === 0 ? textColor : textColor2;
          if (maskData) {
            // Sample the center of the character
            const sampleX = Math.floor(Math.min(Math.max(x + charInfo.width / 2, 0), CANVAS_WIDTH - 1));
            const sampleY = Math.floor(Math.min(Math.max(y - fontSize / 2, 0), CANVAS_HEIGHT - 1));
            const index = (sampleY * CANVAS_WIDTH + sampleX) * 4;
            // If the red channel is high (white), it's inside the calligram
            if (maskData.data[index] > 128) {
              color = calligramColor;
            }
          }
          
          ctx.fillStyle = color;
          ctx.fillText(charInfo.char, x, y);
          
          x += charInfo.width + spacing;
        }
        
        y += fontSize * LINE_SPACING;
      }

    }, [markdownText, calligramText, bgColor, textColor, textColor2, calligramColor]);

    return (
      <div className="w-full flex justify-center bg-base-200 p-4 rounded-xl shadow-inner overflow-hidden">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="w-full max-w-4xl h-auto shadow-lg bg-white object-contain"
          style={{ aspectRatio: `${CANVAS_WIDTH}/${CANVAS_HEIGHT}` }}
        />
      </div>
    );
  }
);

WordArtCanvas.displayName = 'WordArtCanvas';
