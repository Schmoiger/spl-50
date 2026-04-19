import { lexer } from 'marked';
const markdown = `
      # Heading 1
      
      This is a **bold** and *italic* test.
      
      * List item 1
      * List item **2**
    `;
console.log(JSON.stringify(lexer(markdown), null, 2));
