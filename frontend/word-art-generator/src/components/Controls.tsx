import React, { ChangeEvent, useRef, useEffect } from 'react';
import { Upload, Download, Type, Image as ImageIcon, X, CheckSquare, LayoutTemplate } from 'lucide-react';

interface ControlsProps {
  onMarkdownUpload: (content: string) => void;
  orientation: 'landscape' | 'portrait';
  setOrientation: (val: 'landscape' | 'portrait') => void;
  useTextMask: boolean;
  setUseTextMask: (val: boolean) => void;
  useImageMask: boolean;
  setUseImageMask: (val: boolean) => void;
  textPosition: 'center' | 'above' | 'below';
  setTextPosition: (val: 'center' | 'above' | 'below') => void;
  calligramText: string;
  setCalligramText: (text: string) => void;
  maskImage: string | null;
  setMaskImage: (image: string | null) => void;
  maskThreshold: number;
  setMaskThreshold: (val: number) => void;
  maskInvert: boolean;
  setMaskInvert: (val: boolean) => void;
  bgColor: string;
  setBgColor: (color: string) => void;
  textColor: string;
  setTextColor: (color: string) => void;
  textColor2: string;
  setTextColor2: (color: string) => void;
  calligramColor: string;
  setCalligramColor: (color: string) => void;
  onExport: () => void;
  markdownText: string;
}

export function Controls({
  onMarkdownUpload,
  orientation,
  setOrientation,
  useTextMask,
  setUseTextMask,
  useImageMask,
  setUseImageMask,
  textPosition,
  setTextPosition,
  calligramText,
  setCalligramText,
  maskImage,
  setMaskImage,
  maskThreshold,
  setMaskThreshold,
  maskInvert,
  setMaskInvert,
  bgColor,
  setBgColor,
  textColor,
  setTextColor,
  textColor2,
  setTextColor2,
  calligramColor,
  setCalligramColor,
  onExport,
  markdownText,
}: ControlsProps) {
  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const text = evt.target?.result;
        if (typeof text === 'string') {
          onMarkdownUpload(text);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleImageUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        const dataUrl = evt.target?.result;
        if (typeof dataUrl === 'string') {
          setMaskImage(dataUrl);
          
          // Auto-detect background color
          const img = new Image();
          img.onload = () => {
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext('2d');
            if (ctx) {
              ctx.drawImage(img, 0, 0);
              // Background color detection logic removed to satisfy linter (not currently used)
            }
          };
          img.src = dataUrl;
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const previewCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (maskImage && previewCanvasRef.current) {
      const canvas = previewCanvasRef.current;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return;
      
      const img = new Image();
      img.onload = () => {
        // Limit preview size
        const MAX_WIDTH = 300;
        const scale = Math.min(1, MAX_WIDTH / img.width);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
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
        ctx.putImageData(imageData, 0, 0);
      };
      img.src = maskImage;
    }
  }, [maskImage, maskThreshold, maskInvert]);

  return (
    <div className="card bg-base-100 shadow-xl p-6 flex flex-col gap-6 w-full max-w-sm">
      <h2 className="text-2xl font-bold text-center">Word Art Setup</h2>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold flex items-center gap-2">
            <LayoutTemplate size={18} /> Canvas Orientation
          </span>
        </label>
        <select 
          value={orientation}
          onChange={(e) => setOrientation(e.target.value as 'landscape' | 'portrait')}
          className="select select-bordered w-full"
        >
          <option value="landscape">Landscape</option>
          <option value="portrait">Portrait</option>
        </select>
      </div>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold flex items-center gap-2">
            <Upload size={18} /> Content
          </span>
        </label>
        <div className="flex flex-col gap-2">
          <input
            type="file"
            accept=".md,.txt"
            onChange={handleFileUpload}
            className="file-input file-input-bordered file-input-primary file-input-sm w-full"
          />
          <textarea
            value={typeof markdownText === 'string' ? markdownText : ''}
            onChange={(e) => onMarkdownUpload(e.target.value)}
            className="textarea textarea-bordered h-32 w-full text-xs font-mono"
            placeholder="Or paste your markdown here..."
          />
        </div>
      </div>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold flex items-center gap-2">
            <CheckSquare size={18} /> Mask Type
          </span>
        </label>
        <div className="flex gap-4 mb-2">
          <label className="cursor-pointer flex items-center gap-2">
            <input 
              type="checkbox" 
              checked={useTextMask}
              onChange={(e) => setUseTextMask(e.target.checked)}
              className="checkbox checkbox-primary checkbox-sm" 
            />
            <span className="label-text">Text</span> 
          </label>
          <label className="cursor-pointer flex items-center gap-2">
            <input 
              type="checkbox" 
              checked={useImageMask}
              onChange={(e) => setUseImageMask(e.target.checked)}
              className="checkbox checkbox-secondary checkbox-sm" 
            />
            <span className="label-text">Image</span> 
          </label>
        </div>
      </div>

      {useTextMask && useImageMask && (
        <div className="form-control w-full">
          <label className="label">
            <span className="label-text font-semibold text-xs">Text Position</span>
          </label>
          <select 
            value={textPosition}
            onChange={(e) => setTextPosition(e.target.value as 'center' | 'above' | 'below')}
            className="select select-bordered select-sm w-full"
          >
            <option value="center">Overlap Center</option>
            <option value="above">Above Image</option>
            <option value="below">Below Image</option>
          </select>
        </div>
      )}

      {useTextMask && (
        <div className="form-control w-full">
          <label className="label">
            <span className="label-text font-semibold flex items-center gap-2">
              <Type size={18} /> Calligram Text
            </span>
          </label>
          <input
            type="text"
            value={calligramText}
            onChange={(e) => setCalligramText(e.target.value)}
            placeholder="e.g. HELLO"
            className="input input-bordered w-full"
          />
        </div>
      )}

      {useImageMask && (
        <div className="form-control w-full">
          <label className="label">
            <span className="label-text font-semibold flex items-center gap-2">
              <ImageIcon size={18} /> Calligram Image Mask
            </span>
          </label>
          {!maskImage ? (
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="file-input file-input-bordered file-input-secondary w-full"
            />
          ) : (
            <div className="flex flex-col gap-4">
              <div className="relative w-full rounded-lg border border-base-300 overflow-hidden bg-base-200 flex items-center justify-center p-2">
                <canvas ref={previewCanvasRef} className="max-h-32 object-contain" />
                <button
                  onClick={() => setMaskImage(null)}
                  className="btn btn-circle btn-xs btn-error absolute top-2 right-2"
                  aria-label="Remove image mask"
                >
                  <X size={14} />
                </button>
              </div>
              
              <div className="form-control w-full">
                <label className="label">
                  <span className="label-text font-semibold text-xs">Threshold ({maskThreshold})</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="255"
                  value={maskThreshold}
                  onChange={(e) => setMaskThreshold(parseInt(e.target.value))}
                  className="range range-xs range-secondary"
                />
              </div>
              
              <label className="cursor-pointer label">
                <span className="label-text font-semibold text-xs">Invert Mask</span> 
                <input 
                  type="checkbox" 
                  checked={maskInvert}
                  onChange={(e) => setMaskInvert(e.target.checked)}
                  className="checkbox checkbox-secondary checkbox-sm" 
                />
              </label>
            </div>
          )}
        </div>
      )}

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold">Background Color</span>
        </label>
        <div className="flex gap-2 items-center">
          <input
            type="color"
            value={bgColor}
            onChange={(e) => setBgColor(e.target.value)}
            className="w-12 h-12 p-1 bg-base-100 border border-base-300 rounded cursor-pointer"
          />
          <span className="font-mono text-sm uppercase">{bgColor}</span>
        </div>
      </div>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold">Base Text Color (Para 1)</span>
        </label>
        <div className="flex gap-2 items-center">
          <input
            type="color"
            value={textColor}
            onChange={(e) => setTextColor(e.target.value)}
            className="w-12 h-12 p-1 bg-base-100 border border-base-300 rounded cursor-pointer"
          />
          <span className="font-mono text-sm uppercase">{textColor}</span>
        </div>
      </div>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold">Alt Text Color (Para 2)</span>
        </label>
        <div className="flex gap-2 items-center">
          <input
            type="color"
            value={textColor2}
            onChange={(e) => setTextColor2(e.target.value)}
            className="w-12 h-12 p-1 bg-base-100 border border-base-300 rounded cursor-pointer"
          />
          <span className="font-mono text-sm uppercase">{textColor2}</span>
        </div>
      </div>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold">Calligram Color</span>
        </label>
        <div className="flex gap-2 items-center">
          <input
            type="color"
            value={calligramColor}
            onChange={(e) => setCalligramColor(e.target.value)}
            className="w-12 h-12 p-1 bg-base-100 border border-base-300 rounded cursor-pointer"
          />
          <span className="font-mono text-sm uppercase">{calligramColor}</span>
        </div>
      </div>

      <button onClick={onExport} className="btn btn-primary w-full gap-2 mt-4">
        <Download size={18} /> Export as PNG
      </button>
    </div>
  );
}
