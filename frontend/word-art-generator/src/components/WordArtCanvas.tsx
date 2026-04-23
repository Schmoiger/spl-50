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
const PADDING = 50; // Safety margin on all sides
const FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const CALLIGRAM_FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const BASE_COLOR = '#91b8a5'; // Sea foam
const CALLIGRAM_COLOR = '#7e22ce'; // Sophisticated purple

export const WordArtCanvas = forwardRef<WordArtCanvasRef, WordArtCanvasProps>(
  ({ markdownText, orientation, useTextMask, useImageMask, textPosition, calligramText, maskImage, maskThreshold = 128, maskInvert = false, bgColor, textColor, textColor2, calligramColor }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    
    const CANVAS_WIDTH = orientation === 'landscape' ? 1200 : 800;
    const CANVAS_HEIGHT = orientation === 'landscape' ? 800 : 1200;
    const SAFE_WIDTH = CANVAS_WIDTH - (PADDING * 2);
    const SAFE_HEIGHT = CANVAS_HEIGHT - (PADDING * 2);

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
      ctx.fillStyle = bgColor || '#fdfcf0';
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      if (!markdownText) return;

      // 2. Parse markdown
      const segments = parseMarkdown(markdownText);
      if (segments.length === 0) return;

      // 3. Helper to draw text once mask is ready
      const drawWithMask = (maskData: ImageData | null) => {
        // 4. Calculate font size
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
        // Use SAFE dimensions for font size calculation
        let fontSize = Math.sqrt((SAFE_WIDTH * SAFE_HEIGHT) / (widthAt1px * LINE_SPACING));
        
        // 5. Layout and Draw text
        interface RenderChar {
          char: string;
          weight: string;
          style: string;
          width: number;
          paragraphIndex: number;
        }

        interface RenderWord {
          chars: RenderChar[];
          width: number;
          isSpace: boolean;
        }
        
        const scaleForMeasuring = 100;
        const baseWords: { chars: any[], width: number, isSpace: boolean }[] = [];
        let tempChars: any[] = [];
        let tempWidth = 0;

        for (const seg of segments) {
          const weight = seg.bold ? 'bold' : 'normal';
          const style = seg.italic ? 'italic' : 'normal';
          measureCtx.font = `${style} ${weight} ${scaleForMeasuring}px ${FONT_FAMILY}`;
          
          for (let i = 0; i < seg.text.length; i++) {
            const char = seg.text[i];
            const width = measureCtx.measureText(char).width / scaleForMeasuring;
            const charInfo = { char, weight, style, width, paragraphIndex: seg.paragraphIndex };

            if (char === ' ') {
              if (tempChars.length > 0) {
                baseWords.push({ chars: tempChars, width: tempWidth, isSpace: false });
                tempChars = [];
                tempWidth = 0;
              }
              baseWords.push({ chars: [charInfo], width, isSpace: true });
            } else {
              tempChars.push(charInfo);
              tempWidth += width;
            }
          }
        }
        if (tempChars.length > 0) {
          baseWords.push({ chars: tempChars, width: tempWidth, isSpace: false });
        }

        const simulateLayout = (fSize: number) => {
          let lines: { words: any[], extraSpace: number }[] = [];
          let currentLine: any[] = [];
          let currentLineWidth = 0;

          for (const word of baseWords) {
            const wordWidth = word.width * fSize;
            if (currentLineWidth + wordWidth > SAFE_WIDTH && currentLine.length > 0) {
              let lineToPush = [...currentLine];
              let lineWidthToPush = currentLineWidth;
              if (lineToPush[lineToPush.length - 1].isSpace) {
                const last = lineToPush.pop()!;
                lineWidthToPush -= last.width * fSize;
              }
              lines.push({ words: lineToPush, extraSpace: SAFE_WIDTH - lineWidthToPush });
              currentLine = [];
              currentLineWidth = 0;
              if (word.isSpace) continue;
            }
            currentLine.push(word);
            currentLineWidth += wordWidth;
          }
          if (currentLine.length > 0) {
            lines.push({ words: currentLine, extraSpace: 0 });
          }
          return { lines, totalHeight: lines.length * (fSize * LINE_SPACING) };
        };

        let minFS = fontSize * 0.5;
        let maxFS = fontSize * 2.0;
        let finalLines: any[] = [];
        
        for (let i = 0; i < 15; i++) { // Increase iterations for better precision
          const midFS = (minFS + maxFS) / 2;
          const { lines, totalHeight } = simulateLayout(midFS);
          if (totalHeight > SAFE_HEIGHT * 0.95) {
            maxFS = midFS;
          } else {
            minFS = midFS;
            fontSize = midFS;
            finalLines = lines;
          }
        }

        // Final drawing loop
        let y = PADDING + fontSize;
        ctx.textBaseline = 'bottom';
        ctx.textAlign = 'left';
        
        for (const line of finalLines) {
          if (y - fontSize > CANVAS_HEIGHT - PADDING) break;
          
          let x = PADDING;
          const spaceWords = line.words.filter(w => w.isSpace);
          const spaceCount = spaceWords.length;
          
          // Determine if this is the last line (extraSpace is 0). If so, do not justify.
          const isLastLine = line.extraSpace === 0;
          const extraSpacePerGap = (!isLastLine && spaceCount > 0) ? line.extraSpace / spaceCount : 0;
          
          for (const word of line.words) {
            for (const charInfo of word.chars) {
              const charWidth = charInfo.width * fontSize;
              ctx.font = `${charInfo.style} ${charInfo.weight} ${fontSize}px ${FONT_FAMILY}`;
              
              let color = charInfo.paragraphIndex % 2 === 0 ? textColor : textColor2;
              if (maskData) {
                const sampleX = Math.floor(Math.min(Math.max(x + charWidth / 2, 0), CANVAS_WIDTH - 1));
                const sampleY = Math.floor(Math.min(Math.max(y - fontSize / 2, 0), CANVAS_HEIGHT - 1));
                const index = (sampleY * CANVAS_WIDTH + sampleX) * 4;
                const inMask = maskData.data[index] > 128;
                if (inMask) color = calligramColor;
              }
              
              ctx.fillStyle = color;
              ctx.fillText(charInfo.char, x, y);
              x += charWidth;
            }
            if (word.isSpace) {
              // The natural width of the space was already added by the inner loop.
              // We only need to add the justification gap.
              x += extraSpacePerGap;
            }
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
