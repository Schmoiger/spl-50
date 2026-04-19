import { useState, useRef } from 'react';
import { Controls } from './components/Controls';
import { WordArtCanvas, type WordArtCanvasRef } from './components/WordArtCanvas';

function App() {
  const [markdownText, setMarkdownText] = useState<string>('# Hello\n\nUpload a markdown file to see the magic happen! **Bold** and *italic* text is supported.');
  const [calligramText, setCalligramText] = useState<string>('ART');
  const [bgColor, setBgColor] = useState<string>('#ffffff');
  const [textColor, setTextColor] = useState<string>('#8e9e9a');
  const [textColor2, setTextColor2] = useState<string>('#7e929f');
  const [calligramColor, setCalligramColor] = useState<string>('#7e22ce');
  const canvasRef = useRef<WordArtCanvasRef>(null);

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
            calligramText={calligramText}
            setCalligramText={setCalligramText}
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
            calligramText={calligramText}
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
