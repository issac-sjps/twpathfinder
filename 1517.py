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

def fetch_1517_data_perfectly():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080") 

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 15)
    all_data = []

    target_url = "https://twpathfinder.org/overview1517"

    try:
        print("【系統啟動】開始執行 15-17 歲專屬資料探勘...")
        driver.get(target_url)
        page = 1
        
        # 建立防呆變數：用來記錄上一頁的第一筆編號
        previous_first_id = None

        # 加入硬性上限：15-17歲僅約 6 頁，設定最多跑 10 頁作為絕對保險絲
        while page <= 10:
            print(f"正在擷取第 {page} 頁資料...")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            time.sleep(2) 

            rows = driver.find_elements(By.XPATH, "//table//tr")[1:] 
            
            # 【核心防護邏輯】：偵測是否抓到重複的頁面
            if len(rows) > 0:
                current_first_cols = rows[0].find_elements(By.TAG_NAME, "td")
                if len(current_first_cols) > 0:
                    current_first_id = current_first_cols[0].text.strip()
                    if current_first_id == previous_first_id:
                        print("【強制中斷】偵測到本頁資料與上一頁重複，網站已達最後一頁。")
                        break
                    previous_first_id = current_first_id

            page_data_count = 0

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 9:
                    download_link = ""
                    try:
                        a_tag = cols[1].find_element(By.TAG_NAME, "a")
                        download_link = a_tag.get_attribute("href")
                    except Exception:
                        pass

                    all_data.append({
                        "id": cols[0].text.strip(),
                        "download_url": download_link,
                        "project_name": cols[2].text.strip(),
                        "city": cols[3].text.strip(),
                        "category": cols[4].text.strip(),
                        "theme": cols[5].text.strip(),
                        "duration": cols[6].text.strip(),
                        "quota": cols[7].text.strip(),
                        "description": cols[8].text.strip()
                    })
                    page_data_count += 1
            
            print(f" -> 取得 {page_data_count} 筆有效資料。")

            try:
                next_btn = driver.find_element(By.XPATH, "//a[contains(text(), '下一頁')]")
                
                # 雙重防護：檢查按鈕是否有實質的 href 連結，或是否被標記為 disabled
                href = next_btn.get_attribute("href")
                class_name = next_btn.get_attribute("class") or ""
                
                if "disabled" in class_name or not href:
                    print("【判定】下一頁按鈕已失效，已抵達最終頁。")
                    break

                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3) 
                page += 1
            except Exception:
                print("【判定】未發現下一頁按鈕，擷取完畢。")
                break

        if all_data:
            with open("pathfinder_data_1517.json", "w", encoding="utf-8") as json_file:
                json.dump(all_data, json_file, ensure_ascii=False, indent=4)
            
            df = pd.DataFrame(all_data)
            df.to_csv("pathfinder_data_1517.csv", index=False, encoding="utf-8-sig")
            
            print(f"\n【任務完美達成】成功抓取 {len(all_data)} 筆 15-17 歲資料。")
            print("檔案已覆蓋更新：pathfinder_data_1517.json")
        else:
            print("\n【失敗】未抓取到有效資料。")

    except Exception as e:
        print(f"【系統崩潰】錯誤：{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_1517_data_perfectly()