import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


TARGET_BRANDS = [
    "뉴발란스",
    "아식스",
    "나이키",
    "살로몬"
]

SCROLL_COUNT = 1

MAX_PRODUCTS_PER_BRAND = 1

def create_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")

    options.add_argument(
        "user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        options=options
    )

    return driver


def crawl_soldout(driver):
    results = []

    for brand in TARGET_BRANDS:

        print(
            f"\n=== [{brand}] "
            f"신발 목록 수집 중... ==="
        )

        search_url = (
            "https://www.soldout.co.kr/"
            "search/product/list"
            f"?top_category=1&keyword={brand}"
        )

        driver.get(search_url)

        time.sleep(5)

        for _ in range(SCROLL_COUNT):
            driver.find_element(
                By.TAG_NAME,
                "body"
            ).send_keys(Keys.END)

            time.sleep(2)

        cards = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/trade/detail/') "
            "or contains(@href, '/product/')]"
        )

        print(
            f"-> [{brand}] 발견된 카드 수: "
            f"{len(cards)}개"
        )

        collected_count = 0

        for card in cards:

            try:
                url = card.get_attribute("href")

                if not url:
                    continue

                if "/search/product/" in url:
                    continue

                if (
                    "/trade/detail/" not in url
                    and "/product/" not in url
                ):
                    continue

                card_text = card.text.strip()

                if not card_text:
                    continue

                lines = [
                    line.strip()
                    for line in card_text.split("\n")
                    if line.strip()
                ]

                product_name = "N/A"
                buy_price = "N/A"
                trade_price = "N/A"

                if len(lines) >= 2:
                    product_name = lines[1]

                for line in lines:
                    if "원" in line:
                        if buy_price == "N/A":
                            buy_price = line

                detail_url = url
                driver.get(detail_url)

                time.sleep(5)

                driver.find_element(
                    By.TAG_NAME,
                    "body"
                ).send_keys(Keys.END)

                time.sleep(2)

                detail_text = driver.find_element(
                    By.TAG_NAME,
                    "body"
                ).text

                detail_lines = [
                    line.strip()
                    for line in detail_text.split("\n")
                    if line.strip()
                ]

                for i, line in enumerate(detail_lines):
                    if line == "즉시 구매가":
                        if i >= 2:
                            buy_price = detail_lines[i - 2] + "원"
                        break

                for i, line in enumerate(detail_lines):
                    if line == "최근 거래가":
                        if i + 1 < len(detail_lines):
                            trade_price = detail_lines[i + 1]
                        break


                print(f"[즉시 구매가] {buy_price}")
                print(f"[최근 거래가] {trade_price}")

                results.append({
                    "브랜드명": brand,
                    "상품명": product_name,
                    "즉시구매가": buy_price,
                    "최근거래가": trade_price,
                    "URL": url
                })

                collected_count += 1

                if collected_count >= MAX_PRODUCTS_PER_BRAND:
                    break

            except Exception:
                continue

    return results


def save_raw_data(results):
    df = pd.DataFrame(results)

    print("\n[TEST] 중복 제거 전 수집 결과")
    print(df)

    df = df.drop_duplicates(
        subset=["URL"]
    )

    df.to_csv(
    "data/raw/soldout_raw.csv",
    index=False,
    encoding="utf-8-sig"
    )

    print(
        f"\n[INFO] Raw 데이터 저장 완료: "
        f"{len(df):,}건"
    )

    return df


if __name__ == "__main__":

    driver = create_driver()

    try:

        results = crawl_soldout(
            driver
        )

        df = save_raw_data(
            results
        )

        print(
            f"\n[INFO] 총 저장 데이터: "
            f"{len(df):,}건"
        )

    finally:

        driver.quit()