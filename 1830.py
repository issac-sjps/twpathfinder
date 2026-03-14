import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_all_data_for_spa():
    # 設定 Chrome (Chrome) 瀏覽器選項
    chrome_options = Options()
    chrome_options.add_argument("--headless") # 無頭模式，隱藏 UI (User Interface)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") 

    # 初始化 WebDriver (WebDriver)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)
    all_data = []
    base_url = "https://twpathfinder.org/overview1830"

    try:
        print("【系統啟動】開始執行全欄位與下載連結爬取任務...")
        driver.get(base_url)

        for page in range(1, 12):
            print(f"正在擷取第 {page} 頁資料...")

            # 等待表格本體出現
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(2) 

            rows = driver.find_elements(By.XPATH, "//table//tr")[1:] 
            page_data_count = 0

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if len(cols) >= 9:
                    # 針對「下載」欄位進行特殊處理：提取 <a> 標籤內的 href (Hypertext Reference) 屬性
                    download_link = ""
                    try:
                        # 尋找該儲存格內的連結元素
                        a_tag = cols[1].find_element(By.TAG_NAME, "a")
                        download_link = a_tag.get_attribute("href")
                    except Exception:
                        # 防呆機制：若該計畫無下載連結，則保留空字串，防止程式崩潰
                        pass

                    all_data.append({
                        "id": cols[0].text.strip(),                       # 編號
                        "download_url": download_link,                    # 下載連結
                        "project_name": cols[2].text.strip(),             # 計畫名稱
                        "city": cols[3].text.strip(),                     # 城市
                        "category": cols[4].text.strip(),                 # 計畫主題類別
                        "theme": cols[5].text.strip(),                    # 主題
                        "duration": cols[6].text.strip(),                 # 圓夢期間
                        "quota": cols[7].text.strip(),                    # 名額
                        "description": cols[8].text.strip()               # 圓夢機會簡述
                    })
                    page_data_count += 1
            
            print(f" -> 第 {page} 頁解析完畢，取得 {page_data_count} 筆完整資料。")

            if page < 11:
                try:
                    next_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '下一頁')]")))
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(3) 
                except Exception as e:
                    print(f"【嚴重警告】第 {page} 頁翻頁失敗：{e}")
                    break

        if all_data:
            # 輸出為 JSON (JavaScript Object Notation)，供一頁式網站直接讀取
            with open("pathfinder_data.json", "w", encoding="utf-8") as json_file:
                json.dump(all_data, json_file, ensure_ascii=False, indent=4)
            
            # 輸出為 CSV (Comma-Separated Values) 作為本地資料庫備份
            df = pd.DataFrame(all_data)
            df.to_csv("pathfinder_data.csv", index=False, encoding="utf-8-sig")
            
            print(f"\n【任務完美達成】共抓取 {len(all_data)} 筆資料。")
            print("檔案已產出：pathfinder_data.json (前端用) 與 pathfinder_data.csv (備份用)。")
        else:
            print("\n【失敗】未抓取到有效資料。")

    except Exception as e:
        print(f"【系統崩潰】錯誤：{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_all_data_for_spa()