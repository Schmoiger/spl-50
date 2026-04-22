import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import { parseMarkdown, type TextSegment } from '../utils/markdownParser';

interface WordArtCanvasProps {
  markdownText: string;
  orientation: 'landscape' | 'portrait';
  useTextMask: boolean;
  useImageMask: boolean;
  textPosition: 'center' | 'above' | 'below';
  calligramText: string;
  maskImage: string | null;
  maskThreshold?: number;
  maskInvert?: boolean;
  bgColor: string;
  textColor: string;
  textColor2: string;
  calligramColor: string;
}

export interface WordArtCanvasRef {
  exportToPNG: () => void;
}

const LINE_SPACING = 1.1; // Line height multiplier
const FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const CALLIGRAM_FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const BASE_COLOR = '#8e9e9a'; // Comforting grey (sea foam hint)
const CALLIGRAM_COLOR = '#7e22ce'; // Sophisticated purple

export const WordArtCanvas = forwardRef<WordArtCanvasRef, WordArtCanvasProps>(
  ({ markdownText, orientation, useTextMask, useImageMask, textPosition, calligramText, maskImage, maskThreshold = 128, maskInvert = false, bgColor, textColor, textColor2, calligramColor }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    
    const CANVAS_WIDTH = orientation === 'landscape' ? 1200 : 800;
    const CANVAS_HEIGHT = orientation === 'landscape' ? 800 : 1200;

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

      // 3. Helper to draw text once mask is ready
      const drawWithMask = (maskData: ImageData | null) => {
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
              
              // The mask is pre-processed into pure black & white.
              // We just check if the pixel is white (red channel > 128).
              const inMask = maskData.data[index] > 128;
                
              if (inMask) {
                color = calligramColor;
              }
            }
            
            ctx.fillStyle = color;
            ctx.fillText(charInfo.char, x, y);
            
            x += charInfo.width + spacing;
          }
          
          y += fontSize * LINE_SPACING;
        }
      };

      // 6. Create calligram mask
      const maskCanvas = document.createElement('canvas');
      maskCanvas.width = CANVAS_WIDTH;
      maskCanvas.height = CANVAS_HEIGHT;
      const maskCtx = maskCanvas.getContext('2d', { willReadFrequently: true });
      
      if (!maskCtx || (!useImageMask && !useTextMask)) {
        drawWithMask(null);
        return;
      }

      const drawTextOnMask = () => {
        if (useTextMask && calligramText) {
          maskCtx.fillStyle = 'white';
          maskCtx.textAlign = 'center';
          maskCtx.textBaseline = 'middle';
          
          let cSize = 500;
          maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
          while (maskCtx.measureText(calligramText).width > CANVAS_WIDTH * 0.9 && cSize > 50) {
            cSize -= 10;
            maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
          }
          
          let y = CANVAS_HEIGHT / 2;
          if (useImageMask && maskImage && textPosition !== 'center') {
            if (textPosition === 'above') y = CANVAS_HEIGHT * 0.1;
            if (textPosition === 'below') y = CANVAS_HEIGHT * 0.9;
          }
          
          maskCtx.fillText(calligramText, CANVAS_WIDTH / 2, y);
        }
        
        const maskData = maskCtx.getImageData(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        drawWithMask(maskData);
      };

      maskCtx.fillStyle = 'black';
      maskCtx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      if (useImageMask && maskImage) {
        const img = new Image();
        img.onload = () => {
          let availableHeight = CANVAS_HEIGHT;
          let imageYOffset = 0;
          
          if (useTextMask && calligramText && textPosition !== 'center') {
            availableHeight = CANVAS_HEIGHT * 0.8;
            if (textPosition === 'above') imageYOffset = CANVAS_HEIGHT * 0.2;
          }

          const scale = Math.min(CANVAS_WIDTH / img.width, availableHeight / img.height) * 0.9;
          const w = img.width * scale;
          const h = img.height * scale;
          const x = (CANVAS_WIDTH - w) / 2;
          const y = imageYOffset + (availableHeight - h) / 2;
          
          maskCtx.drawImage(img, x, y, w, h);
          const imageData = maskCtx.getImageData(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
          
          for (let i = 0; i < imageData.data.length; i += 4) {
            const r = imageData.data[i];
            const g = imageData.data[i + 1];
            const b = imageData.data[i + 2];
            const a = imageData.data[i + 3];
            
            const brightness = (r * 299 + g * 587 + b * 114) / 1000;
            let inMask = false;
            
            if (a > 50) {
              const isDarkEnough = brightness < maskThreshold;
              inMask = maskInvert ? !isDarkEnough : isDarkEnough;
            }
            
            const color = inMask ? 255 : 0;
            imageData.data[i] = color;
            imageData.data[i + 1] = color;
            imageData.data[i + 2] = color;
            imageData.data[i + 3] = 255;
          }
          maskCtx.putImageData(imageData, 0, 0);
          
          drawTextOnMask();
        };
        img.src = maskImage;
      } else {
        drawTextOnMask();
      }

    }, [markdownText, orientation, useTextMask, useImageMask, textPosition, calligramText, maskImage, maskThreshold, maskInvert, bgColor, textColor, textColor2, calligramColor]);

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
