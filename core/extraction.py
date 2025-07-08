from PIL import Image, ImageEnhance
from typing import List, Dict
from core.data import get_recipes
from core.utils import normalize_str
from config import logger
from collections import defaultdict
from Levenshtein import distance as levenshtein_distance
import copy
import cv2
import numpy as np
import pytesseract


def preprocess_menu(
    image: Image.Image,
    threshold: float = 220,
    contrast: float = 2.0,
    ) -> Image.Image:
    _image = image.convert("L")
    enhancer = ImageEnhance.Contrast(_image)
    _image = enhancer.enhance(contrast)
    _image = _image.point(lambda p: p > threshold and 255)
    return _image


def preprocess_image(image: Image.Image) -> Image.Image:
    _image = image.convert("L")
    _image = np.array(_image)

    cv_image_color = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    blurred = cv2.GaussianBlur(_image, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    menu_crop = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w < 100 or h < 100:
            continue

        if x < _image.shape[1] * 0.3:
            continue

        aspect_ratio = w / float(h)

        if 0.3 < aspect_ratio < 1.8:
            menu_crop = cv_image_color[y:y+h, x:x+w]
            break
    if menu_crop is not None:
        menu_pil = Image.fromarray(cv2.cvtColor(menu_crop, cv2.COLOR_BGR2RGB))
        return menu_pil
    else:
        return image


def extract_ingredients_from_image(image: Image.Image, raw: bool = False) -> List[str]:
    _image = copy.deepcopy(image)
    # _image = preprocess_image(_image)
    _image = preprocess_menu(_image)
    text = pytesseract.image_to_string(_image)
    if raw:
        return [text]
    text = text.replace("\n\n", "\n")
    text = "\n".join([" ".join([s for s in t.split(" ") if len(s) > 2]) for t in text.split("\n")])

    text = text.split("\n")
    text = [normalize_str(t) for t in text if len(t) > 2]

    logger.debug(f"Extracted ingredients: {text}")
    return text


def extract_ingredients_from_images(images: List[Image.Image]) -> List[str]:
    ingredients = []
    for image in images:
        ingredients.extend(extract_ingredients_from_image(image))
    return ingredients


def extract_recipes_from_images(images: List[Image.Image], n_chefs: int) -> List[Dict[str, str]]:
    n_chefs = n_chefs - 1
    norm_ingredients = extract_ingredients_from_images(images)
    chef_data = get_recipes()[n_chefs]

    available_types = defaultdict(list)
    for ingredient in chef_data["ingredients"]:
        if not any(levenshtein_distance(norm_ingredient, ingredient["norm_name"]) < 3 for norm_ingredient in norm_ingredients):
            continue

        available_types[ingredient["type"]].append(ingredient["name"])
    logger.debug(f"Available types of ingredients: {available_types}")
    
    available_recipes = list()
    for meal in chef_data["meals"]:
        type1 = meal["ingredient1"]
        type2 = meal["ingredient2"]

        if type1 not in available_types or type2 not in available_types:
            continue

        if type1 == type2:
            if len(available_types[type1]) < 2:
                continue

            available_recipes.append({
                "ingredient1": available_types[type1][0],
                "ingredient2": available_types[type1][1],
                "effect": meal["effect"]
            })
            continue

        available_recipes.append({
            "ingredient1": available_types[type1][0],
            "ingredient2": available_types[type2][0],
            "effect": meal["effect"]
        })
    logger.debug(f"Extracted recipes: {available_recipes}")
    
    return available_recipes
