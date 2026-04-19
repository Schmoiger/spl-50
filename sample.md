# Welcome to Word Art Generator

This is a **sample text** that we will use to *test* the word art generation. It should fit inside the canvas, and when it wraps around it should ignore the newlines and just keep rendering. The word art is designed to look like a calligram, which means a secret word or image is hidden inside the text.

If you look closely, you should be able to see the word **ART** embedded in this sea of text. It uses a **sophisticated purple** colour against a *comforting sea foam grey*.

Let's add some more text so that the canvas is fully populated. We want to ensure that the font sizing algorithm correctly calculates the optimal font size to perfectly fit all the characters in the available space. The algorithm does this by measuring the total width of all characters if they were laid out on a single line at a base font size, and then solving a quadratic equation to find the exact font size that will result in the total area matching the canvas area, taking into account the line height spacing.

Isn't that neat? By the way, the system is built with Vite, React, TailwindCSS, and DaisyUI. It uses HTML5 Canvas API with an offscreen mask buffer to compute pixel collisions and determine which color to use for each character based on its exact position on the canvas. This allows the mask to be virtually anything - a word, a sentence, or even a black and white image.

Thanks for testing this application!
