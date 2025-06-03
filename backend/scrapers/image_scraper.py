from bs4 import BeautifulSoup
import requests

def get_first_image_url(listing_url: str) -> str:
    response = requests.get(listing_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        # Option 1: Try OpenGraph (used by many sites)
        og_image = soup.find("meta", property="og:image")
        if og_image:
            return og_image["content"]

        # Option 2: Fallback: first <img> tag
        img_tag = soup.find("img")
        if img_tag and "src" in img_tag.attrs:
            return img_tag["src"]

        return None  # No image found
    except:
        return None
    
if __name__ == "__main__":
    print(get_first_image_url("https://www.padmapper.com/buildings/p302063/apartments-at-57-charles-st-w-toronto-on-m5s-2x1"))