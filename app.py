from scrapers.kijiji_scraper import get_kijiji_driver

driver = get_kijiji_driver()
driver.get("https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273")

print(driver.title)  # Should print the title of the page

driver.quit()  # Always quit when done