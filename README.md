# mhfu-recipe-book

A tool for Monster Hunter Freedom Unite that uses computer vision to detect available recipes from the in-game canteen menu.

<div class="holder">
    <img src="./source/mhfu-recipe-book.gif"/>
</div>

## Overview

This project provides a transparent, resizable window that can be placed over the game's canteen menu. The tool allows you to capture screenshots of the menu, detect the visible ingredients, and display the possible meals (recipes) that the Felynes can prepare, along with their effects.

## Features

- **Transparent Screenshot Window:** Overlay the window on the game to capture only the relevant area.
- **Add Images Button:** Capture screenshots of the canteen menu. Each click adds a new image to the cache.
- **Recicle Button:** A (poorly designed) recycle button is available to clear all captured images from the cache.
- **Chef Counter:** Use the counter to select the number of chefs (Felynes) for the meal.
- **Recipes Button:** After capturing images, click this button to process the images and display a popup with the detected recipes and their effects.
- **Popup Display:** Recipes and their effects are shown in a scrollable popup window for easy viewing.

## Usage

1. Start the tool and position the transparent window over the Monster Hunter Freedom Unite canteen menu.
2. Use the **add** button to capture images of the menu.
3. Adjust the **chef counter** to match the number of chefs.
4. Use the **recicle** button (♲) to clear images if needed.
5. Click the **recipes** button to analyze the captured images and view the possible meal effects.

## Requirements

- Python 3.x
- See `requirements.txt` for dependencies.
- **Tesseract-OCR**: This project uses Tesseract for optical character recognition. You must install Tesseract separately. Download it from [here](https://github.com/UB-Mannheim/tesseract/wiki).
    - By default, the project looks for *Tesseract at C:\Program Files\Tesseract-OCR\tesseract.exe* on Windows. If you install it elsewhere, update the path in main.py accordingly.

## Notes

- The tool is designed specifically for Monster Hunter Freedom Unite.
- The UI is functional but may have some rough edges (especially the recycle button).