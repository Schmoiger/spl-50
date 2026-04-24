import { useEffect, useRef, useImperativeHandle, forwardRef, useCallback } from 'react';
import { parseMarkdown, type TextSegment } from '../utils/markdownParser';

interface WordArtCanvasProps {
  markdownText: string;
  orientation: 'landscape' | 'portrait';
  useTextMask: boolean;
  useImageMask: boolean;
  calligramTextAbove: string;
  calligramTextBelow: string;
  maskImage: string | null;
  maskThreshold?: number;
  maskInvert?: boolean;
  bgColor: string;
  textColor: string;
  textColor2: string;
  calligramColor: string;
}

export interface WordArtCanvasRef {
  exportToPNG: (scaleMultiplier?: number) => Promise<void>;
}

const LINE_SPACING = 1.1; // Line height multiplier
const PADDING = 50; // Safety margin on all sides
const FONT_FAMILY = 'Inter, -apple-system, sans-serif';
const CALLIGRAM_FONT_FAMILY = 'Inter, -apple-system, sans-serif';

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

interface RenderLine {
  words: RenderWord[];
  extraSpace: number;
}

function processSegment(seg: TextSegment, measureCtx: CanvasRenderingContext2D, baseWords: RenderWord[], tempState: { chars: RenderChar[], width: number }) {
  const SCALE_FOR_MEASURING = 100;
  const weight = seg.bold ? 'bold' : 'normal';
  const style = seg.italic ? 'italic' : 'normal';
  measureCtx.font = `${style} ${weight} ${SCALE_FOR_MEASURING}px ${FONT_FAMILY}`;
  
  for (const char of seg.text) {
    const width = measureCtx.measureText(char).width / SCALE_FOR_MEASURING;
    const charInfo = { char, weight, style, width, paragraphIndex: seg.paragraphIndex };

    if (char === ' ') {
      if (tempState.chars.length > 0) {
        baseWords.push({ chars: tempState.chars, width: tempState.width, isSpace: false });
        tempState.chars = [];
        tempState.width = 0;
      }
      baseWords.push({ chars: [charInfo], width, isSpace: true });
    } else {
      tempState.chars.push(charInfo);
      tempState.width += width;
    }
  }
}

function createBaseWords(segments: TextSegment[], measureCtx: CanvasRenderingContext2D): RenderWord[] {
  const baseWords: RenderWord[] = [];
  const tempState = { chars: [] as RenderChar[], width: 0 };

  for (const seg of segments) {
    processSegment(seg, measureCtx, baseWords, tempState);
  }
  
  if (tempState.chars.length > 0) {
    baseWords.push({ chars: tempState.chars, width: tempState.width, isSpace: false });
  }
  return baseWords;
}

function calculateLayout(baseWords: RenderWord[], fSize: number, safeWidth: number): { lines: RenderLine[], totalHeight: number } {
  const lines: RenderLine[] = [];
  let currentLine: RenderWord[] = [];
  let currentLineWidth = 0;

  for (const word of baseWords) {
    const wordWidth = word.width * fSize;
    if (currentLineWidth + wordWidth > safeWidth && currentLine.length > 0) {
      const lineToPush = [...currentLine];
      let lineWidthToPush = currentLineWidth;
      const lastWord = lineToPush.at(-1);
      if (lastWord?.isSpace) {
        lineToPush.pop();
        lineWidthToPush -= lastWord.width * fSize;
      }
      lines.push({ words: lineToPush, extraSpace: safeWidth - lineWidthToPush });
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
}

interface RenderConfig {
  canvasWidth: number;
  canvasHeight: number;
  padding: number;
  lineSpacing: number;
  textColor: string;
  textColor2: string;
  calligramColor: string;
}

function getCharColor(
  charInfo: RenderChar,
  drawX: number,
  drawY: number,
  charWidth: number,
  fontSize: number,
  maskData: ImageData | null,
  config: RenderConfig
): string {
  const baseColor = charInfo.paragraphIndex % 2 === 0 ? config.textColor : config.textColor2;
  if (!maskData) return baseColor;

  const sampleX = Math.floor(Math.min(Math.max(drawX + charWidth / 2, 0), config.canvasWidth - 1));
  const sampleY = Math.floor(Math.min(Math.max(drawY - fontSize / 2, 0), config.canvasHeight - 1));
  const index = (sampleY * config.canvasWidth + sampleX) * 4;
  
  return maskData.data[index] > 128 ? config.calligramColor : baseColor;
}

function renderLine(
  ctx: CanvasRenderingContext2D,
  line: RenderLine,
  drawY: number,
  fontSize: number,
  maskData: ImageData | null,
  config: RenderConfig
) {
  let drawX = config.padding;
  const spaceCount = line.words.filter(w => w.isSpace).length;
  const isLastLine = line.extraSpace === 0;
  const extraSpacePerGap = (!isLastLine && spaceCount > 0) ? line.extraSpace / spaceCount : 0;
  
  for (const word of line.words) {
    for (const charInfo of word.chars) {
      const charWidth = charInfo.width * fontSize;
      ctx.font = `${charInfo.style} ${charInfo.weight} ${fontSize}px ${FONT_FAMILY}`;
      ctx.fillStyle = getCharColor(charInfo, drawX, drawY, charWidth, fontSize, maskData, config);
      ctx.fillText(charInfo.char, drawX, drawY);
      drawX += charWidth;
    }
    if (word.isSpace) {
      drawX += extraSpacePerGap;
    }
  }
}

function renderLayout(
  ctx: CanvasRenderingContext2D, 
  finalLines: RenderLine[], 
  fontSize: number, 
  maskData: ImageData | null,
  config: RenderConfig
) {
  let drawY = config.padding + fontSize;
  ctx.textBaseline = 'bottom';
  ctx.textAlign = 'left';
  
  for (const line of finalLines) {
    if (drawY - fontSize > config.canvasHeight - config.padding) break;
    renderLine(ctx, line, drawY, fontSize, maskData, config);
    drawY += fontSize * config.lineSpacing;
  }
}

export const WordArtCanvas = forwardRef<WordArtCanvasRef, WordArtCanvasProps>(
  ({ markdownText, orientation, useTextMask, useImageMask, calligramTextAbove, calligramTextBelow, maskImage, maskThreshold = 128, maskInvert = false, bgColor, textColor, textColor2, calligramColor }, ref) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    
    const BASE_WIDTH = orientation === 'landscape' ? 1240 : 877;
    const BASE_HEIGHT = orientation === 'landscape' ? 877 : 1240;

    const renderWordArt = useCallback(async (targetCanvas: HTMLCanvasElement, multiplier: number = 1) => {
      const width = BASE_WIDTH * multiplier;
      const height = BASE_HEIGHT * multiplier;
      const padding = PADDING * multiplier;
      const safeWidth = width - (padding * 2);
      const safeHeight = height - (padding * 2);

      targetCanvas.width = width;
      targetCanvas.height = height;
      const ctx = targetCanvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;

      // 1. Clear background
      ctx.fillStyle = bgColor || '#fdfcf0';
      ctx.fillRect(0, 0, width, height);

      if (!markdownText) return;

      // 2. Parse markdown
      const segments = parseMarkdown(markdownText);
      if (segments.length === 0) return;

      // 3. Helper to draw text once mask is ready
      const drawWithMask = (maskData: ImageData | null) => {
        // 4. Calculate font size
        const baseSize = 100;
        let totalBaseWidth = 0;
        
        const measureCtx = document.createElement('canvas').getContext('2d');
        if (!measureCtx) return;

        for (const seg of segments) {
          const weight = seg.bold ? 'bold' : 'normal';
          const style = seg.italic ? 'italic' : 'normal';
          measureCtx.font = `${style} ${weight} ${baseSize}px ${FONT_FAMILY}`;
          totalBaseWidth += measureCtx.measureText(seg.text).width;
        }
        
        const widthAt1px = totalBaseWidth / baseSize;
        // Use SAFE dimensions for font size calculation
        let fontSize = Math.sqrt((safeWidth * safeHeight) / (widthAt1px * LINE_SPACING));
        
        const baseWords = createBaseWords(segments, measureCtx);

        let minFS = fontSize * 0.5;
        let maxFS = fontSize * 2;
        let finalLines: RenderLine[] = [];
        
        for (let i = 0; i < 15; i++) { // Increase iterations for better precision
          const midFS = (minFS + maxFS) / 2;
          const { lines, totalHeight } = calculateLayout(baseWords, midFS, safeWidth);
          if (totalHeight > safeHeight) {
            maxFS = midFS;
          } else {
            minFS = midFS;
            fontSize = midFS;
            finalLines = lines;
          }
        }

        // Final drawing loop
        renderLayout(ctx, finalLines, fontSize, maskData, {
          canvasWidth: width,
          canvasHeight: height,
          padding: padding,
          lineSpacing: LINE_SPACING,
          textColor,
          textColor2,
          calligramColor
        });
      };

      // 6. Create calligram mask
      const maskCanvas = document.createElement('canvas');
      maskCanvas.width = width;
      maskCanvas.height = height;
      const maskCtx = maskCanvas.getContext('2d', { willReadFrequently: true });
      
      if (!maskCtx || (!useImageMask && !useTextMask)) {
        drawWithMask(null);
        return;
      }

      const hasAboveText = useTextMask && calligramTextAbove.trim() !== '';
      const hasBelowText = useTextMask && calligramTextBelow.trim() !== '';

      const drawTextOnMask = () => {
        if (!useTextMask) {
          const maskData = maskCtx.getImageData(0, 0, width, height);
          drawWithMask(maskData);
          return;
        }

        const drawCenteredText = (text: string, yPos: number, maxH: number, baseline: CanvasTextBaseline = 'middle') => {
          maskCtx.fillStyle = 'white';
          maskCtx.textAlign = 'center';
          maskCtx.textBaseline = baseline;
          let cSize = 500 * multiplier;
          maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
          while ((maskCtx.measureText(text).width > width * 0.9 || cSize > maxH) && cSize > 5) {
            cSize -= 5;
            maskCtx.font = `900 ${cSize}px ${CALLIGRAM_FONT_FAMILY}`;
          }
          
          if (baseline === 'bottom') {
            const metrics = maskCtx.measureText(text);
            const descent = metrics.actualBoundingBoxDescent || (cSize * 0.25);
            yPos -= descent;
          }
          
          maskCtx.fillText(text, width / 2, yPos);
        };

        const breathingRoom = height * 0.03;
        const yAbove = padding + breathingRoom;
        const yBelow = height - padding - breathingRoom;
        const maxTextHeight = height * 0.10;
        
        if (!useImageMask || !maskImage) {
           if (hasAboveText && !hasBelowText) {
             drawCenteredText(calligramTextAbove, height / 2, height * 0.9, 'middle');
           } else if (!hasAboveText && hasBelowText) {
             drawCenteredText(calligramTextBelow, height / 2, height * 0.9, 'middle');
           } else if (hasAboveText && hasBelowText) {
             drawCenteredText(calligramTextAbove, height * 0.25, height * 0.4, 'middle');
             drawCenteredText(calligramTextBelow, height * 0.75, height * 0.4, 'middle');
           }
        } else {
           if (hasAboveText) drawCenteredText(calligramTextAbove, yAbove, maxTextHeight, 'top');
           if (hasBelowText) drawCenteredText(calligramTextBelow, yBelow, maxTextHeight, 'bottom');
        }
        
        const maskData = maskCtx.getImageData(0, 0, width, height);
        drawWithMask(maskData);
      };

      maskCtx.clearRect(0, 0, width, height);

      if (useImageMask && maskImage) {
        await new Promise<void>((resolve) => {
          const img = new Image();
          img.onload = () => {
            let availableHeight = height;
            let imageYOffset = 0;
            
            if (hasAboveText && hasBelowText) {
              availableHeight = height * 0.6; // leaves 20% top, 20% bottom
              imageYOffset = height * 0.2;
            } else if (hasAboveText) {
              availableHeight = height * 0.8;
              imageYOffset = height * 0.2;
            } else if (hasBelowText) {
              availableHeight = height * 0.8;
            }

            const scale = Math.min(width / img.width, availableHeight / img.height) * 0.9;
            const w = img.width * scale;
            const h = img.height * scale;
            const x = (width - w) / 2;
            const y = imageYOffset + (availableHeight - h) / 2;
            
            maskCtx.drawImage(img, x, y, w, h);
            const imageData = maskCtx.getImageData(0, 0, width, height);
            
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
            resolve();
          };
          img.src = maskImage;
        });
      } else {
        drawTextOnMask();
      }
    }, [markdownText, useTextMask, useImageMask, calligramTextAbove, calligramTextBelow, maskImage, maskThreshold, maskInvert, bgColor, textColor, textColor2, calligramColor, BASE_WIDTH, BASE_HEIGHT]);

    useImperativeHandle(ref, () => ({
      exportToPNG: async (scaleMultiplier: number = 1) => {
        const tempCanvas = document.createElement('canvas');
        await renderWordArt(tempCanvas, scaleMultiplier);
        const url = tempCanvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = url;
        a.download = `word-art-${scaleMultiplier}x.png`;
        a.click();
      },
    }));

    useEffect(() => {
      const canvas = canvasRef.current;
      if (canvas) {
        renderWordArt(canvas, 1);
      }
    }, [renderWordArt]);

    return (
      <div className="w-full flex justify-center bg-base-200 p-4 rounded-xl shadow-inner overflow-hidden">
        <canvas
          ref={canvasRef}
          width={BASE_WIDTH}
          height={BASE_HEIGHT}
          className="w-full max-w-4xl h-auto shadow-lg bg-white object-contain"
          style={{ aspectRatio: `${BASE_WIDTH}/${BASE_HEIGHT}` }}
        />
      </div>
    );
  }
);

WordArtCanvas.displayName = 'WordArtCanvas';
