from time import time

import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from polimi_scraper.config import LOG_DIR, POLIMAPS_URL, DataPath, logger


def parse_polygons(
    polygons: list[WebElement],
) -> list[tuple[str, list[int], list[int]]]:
    parsed_polygons = []
    for polygon in polygons:
        id_ = polygon.get_attribute("id")
        points = polygon.get_attribute("points")
        x, y = [], []
        for point in points.split():
            point_x, point_y = point.split(",")
            x.append(float(point_x))
            y.append(float(point_y))
        parsed_polygons.append((id_, x, y))
    return parsed_polygons


def get_polygons(driver: Firefox, depth: int = 0):
    polygons = []
    # driver is in the sidebar frame
    if depth == 5:  # We have reached the floor depth in the recursion tree
        driver.switch_to.parent_frame()  # SVG is in the parent frame
        # driver is in the parent frame
        before = time()
        polygons = parse_polygons(driver.find_elements(By.TAG_NAME, "polygon"))
        after = time()
        time_to_find = after - before

        breadcrumb = " > ".join(
            element.text
            for element in driver.find_elements(By.CSS_SELECTOR, "#breadcrumb a")
        )

        logger.info("Looking for SVG in path {}", breadcrumb)
        logger.debug("Took {} s to find polygons", time_to_find)

        # HACK Loading the SVG takes about 3 s, so we can only
        # find polygons this fast if no new data was loaded
        # which represents an error
        if time_to_find < 0.5 or (number_polygons := len(polygons)) == 0:
            logger.warning("No polygons found")
            polygons = []
        else:
            logger.success("Found {} polygons", number_polygons)
        # `driver.back()` only works in the sidebar frame
        # (for whatever reason)
        sidebar_frame = driver.find_element(By.CSS_SELECTOR, "iframe#sidebarFrame")
        driver.switch_to.frame(sidebar_frame)
        # driver is back to the sidebar frame
    else:
        # We can't simply iterate over the links because the DOM is dynamic
        # and references to old links become stale when we go back
        # so we find the links every time and index them manually
        number_links = len(driver.find_elements(By.CSS_SELECTOR, "a.Link"))
        logger.debug("Found {} links at depth {}", number_links, depth)
        for link_index in range(number_links):
            link = driver.find_elements(By.CSS_SELECTOR, "a.Link")[link_index]
            link.click()
            polygons.extend(get_polygons(driver, depth + 1))
            driver.back()
    return polygons


def main():
    logger.add(LOG_DIR / "maps.log", level="INFO")

    driver = Firefox()
    driver.implicitly_wait(10)

    driver.get(POLIMAPS_URL)
    app_frame = driver.find_element(By.CSS_SELECTOR, "iframe#appFrame")
    driver.switch_to.frame(app_frame)
    sidebar_frame = driver.find_element(By.CSS_SELECTOR, "iframe#sidebarFrame")
    driver.switch_to.frame(sidebar_frame)

    try:
        polygons = get_polygons(driver)
    finally:
        driver.close()
        driver.quit()

    polygons_df = pd.DataFrame(
        polygons, columns=["codice_patrimonio", "x", "y"]
    ).drop_duplicates(subset="codice_patrimonio")
    polygons_df

    polygons_df.to_parquet(DataPath.RAW_POLYGONS)


if __name__ == "__main__":
    main()
