import React, { ChangeEvent } from 'react';
import { Upload, Download, Type } from 'lucide-react';

interface ControlsProps {
  onMarkdownUpload: (content: string) => void;
  calligramText: string;
  setCalligramText: (text: string) => void;
  bgColor: string;
  setBgColor: (color: string) => void;
  textColor: string;
  setTextColor: (color: string) => void;
  textColor2: string;
  setTextColor2: (color: string) => void;
  calligramColor: string;
  setCalligramColor: (color: string) => void;
  onExport: () => void;
}

export function Controls({
  onMarkdownUpload,
  calligramText,
  setCalligramText,
  bgColor,
  setBgColor,
  textColor,
  setTextColor,
  textColor2,
  setTextColor2,
  calligramColor,
  setCalligramColor,
  onExport,
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

  return (
    <div className="card bg-base-100 shadow-xl p-6 flex flex-col gap-6 w-full max-w-sm">
      <h2 className="text-2xl font-bold text-center">Word Art Setup</h2>

      <div className="form-control w-full">
        <label className="label">
          <span className="label-text font-semibold flex items-center gap-2">
            <Upload size={18} /> Upload Markdown
          </span>
        </label>
        <input
          type="file"
          accept=".md,.txt"
          onChange={handleFileUpload}
          className="file-input file-input-bordered file-input-primary w-full"
        />
      </div>

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
