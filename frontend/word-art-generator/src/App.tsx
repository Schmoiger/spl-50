import { useState, useRef, useEffect } from 'react';
import { Controls } from './components/Controls';
import { WordArtCanvas, type WordArtCanvasRef } from './components/WordArtCanvas';

function App() {
  const [markdownText, setMarkdownText] = useState<string>('# Hello\n\nUpload a markdown file to see the magic happen! **Bold** and *italic* text is supported.');
  
  const [orientation, setOrientation] = useState<'landscape' | 'portrait'>('landscape');
  const [useTextMask, setUseTextMask] = useState<boolean>(true);
  const [useImageMask, setUseImageMask] = useState<boolean>(true);
  const [textPosition, setTextPosition] = useState<'center' | 'above' | 'below'>('center');
  
  const [calligramText, setCalligramText] = useState<string>('ART');
  const [maskImage, setMaskImage] = useState<string | null>(null);
  const [maskThreshold, setMaskThreshold] = useState<number>(128);
  const [maskInvert, setMaskInvert] = useState<boolean>(false);
  
  const [bgColor, setBgColor] = useState<string>('#ffffff');
  const [textColor, setTextColor] = useState<string>('#8e9e9a');
  const [textColor2, setTextColor2] = useState<string>('#7e929f');
  const [calligramColor, setCalligramColor] = useState<string>('#7e22ce');
  const canvasRef = useRef<WordArtCanvasRef>(null);

  useEffect(() => {
    // Auto-invert the text colors to contrast perfectly with the canvas
    const hex = bgColor.replace('#', '');
    if (hex.length === 6) {
      const r = 255 - parseInt(hex.slice(0, 2), 16);
      const g = 255 - parseInt(hex.slice(2, 4), 16);
      const b = 255 - parseInt(hex.slice(4, 6), 16);
      
      const inverted = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
      setTextColor(inverted);
      
      // TextColor2 is a slightly muted version
      const r2 = Math.max(0, r - 30);
      const g2 = Math.max(0, g - 30);
      const b2 = Math.max(0, b - 30);
      const inverted2 = `#${r2.toString(16).padStart(2, '0')}${g2.toString(16).padStart(2, '0')}${b2.toString(16).padStart(2, '0')}`;
      setTextColor2(inverted2);
    }
  }, [bgColor]);

  const handleExport = () => {
    canvasRef.current?.exportToPNG();
  };

  return (
    <div className="min-h-screen bg-base-200 p-8 flex flex-col items-center gap-8">
      <header className="text-center max-w-2xl">
        <h1 className="text-4xl font-extrabold text-primary mb-4">Word Art Generator</h1>
        <p className="text-base-content/80 text-lg">
          Convert your markdown text into beautiful, landscape word art. 
          Use the calligram feature to reveal hidden words within the text!
        </p>
      </header>

      <main className="w-full max-w-6xl flex flex-col lg:flex-row gap-8 items-start justify-center">
        <div className="w-full lg:w-1/3 flex justify-center">
          <Controls
            onMarkdownUpload={setMarkdownText}
            orientation={orientation}
            setOrientation={setOrientation}
            useTextMask={useTextMask}
            setUseTextMask={setUseTextMask}
            useImageMask={useImageMask}
            setUseImageMask={setUseImageMask}
            textPosition={textPosition}
            setTextPosition={setTextPosition}
            calligramText={calligramText}
            setCalligramText={setCalligramText}
            maskImage={maskImage}
            setMaskImage={setMaskImage}
            maskThreshold={maskThreshold}
            setMaskThreshold={setMaskThreshold}
            maskInvert={maskInvert}
            setMaskInvert={setMaskInvert}
            bgColor={bgColor}
            setBgColor={setBgColor}
            textColor={textColor}
            setTextColor={setTextColor}
            textColor2={textColor2}
            setTextColor2={setTextColor2}
            calligramColor={calligramColor}
            setCalligramColor={setCalligramColor}
            onExport={handleExport}
          />
        </div>
        
        <div className="w-full lg:w-2/3">
          <WordArtCanvas
            ref={canvasRef}
            markdownText={markdownText}
            orientation={orientation}
            useTextMask={useTextMask}
            useImageMask={useImageMask}
            textPosition={textPosition}
            calligramText={calligramText}
            maskImage={maskImage}
            maskThreshold={maskThreshold}
            maskInvert={maskInvert}
            bgColor={bgColor}
            textColor={textColor}
            textColor2={textColor2}
            calligramColor={calligramColor}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
