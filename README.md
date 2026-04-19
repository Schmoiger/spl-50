# Word Art Generator

A premium web application that transforms Markdown text into stunning landscape word art with hidden calligram overlays. 

This project allows you to create dense, visually striking text compositions where a specific word or sentence is "hidden" within a larger body of text using contrasting colors.

## ✨ Features

- **Markdown Support**: Automatically parses bold and italic formatting while stripping away whitespace and newlines for a continuous "sea of text" look.
- **Dynamic Font Scaling**: An intelligent algorithm calculates the optimal font size to perfectly fill the landscape canvas, regardless of the amount of input text.
- **Customizable Calligrams**: Overlay a custom word or sentence that is revealed through a sophisticated color contrast.
- **Full Color Control**: Independently configure the colors for the background, the base text, and the calligram overlay.
- **Premium UI**: Built with a modern, responsive interface using DaisyUI and TailwindCSS.
- **High-Quality Export**: Download your creations as PNG images directly from your browser.

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [Yarn](https://yarnpkg.com/) (Berry/v4)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   yarn install
   ```

### Running Locally

To start the development server for the Word Art Generator:

```bash
yarn workspace word-art-generator dev
```

The app will be available at `http://localhost:5173`.

## 🛠️ Tech Stack

- **Framework**: [React](https://react.dev/) with [Vite](https://vitejs.dev/)
- **Styling**: [TailwindCSS](https://tailwindcss.com/) & [DaisyUI](https://daisyui.com/)
- **Canvas Rendering**: HTML5 Canvas API
- **Markdown Parsing**: [Marked](https://marked.js.org/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Testing**: [Vitest](https://vitest.dev/)

## 📂 Project Structure

- `frontend/word-art-generator/`: The main React application.
- `context/`: Project standards and orchestration context.
- `sample.md`: A sample markdown file provided for testing the generator.
