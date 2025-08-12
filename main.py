from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd, time

# Setup Chrome
options = Options()
options.add_argument('--lang=id')
options.add_argument('accept-language=id-ID, id')
# options.add_argument('--disable-gpu')
# options.add_argument('--window-size=1920x1080')
driver = webdriver.Chrome(options=options)

# Request URL
driver.get('https://www.google.com/maps/place/Graha+Persib/@-6.8997617,107.6075367,17z/data=!3m1!4b1!4m6!3m5!1s0x2e68e64f8431d7a1:0x17a6b97f253f2fc3!8m2!3d-6.899767!4d107.6101116!16s%2Fg%2F1pzppcfq1?entry=ttu&g_ep=EgoyMDI1MDgwNi4wIKXMDSoASAFQAw%3D%3D')
time.sleep(5)

# Klik tombol more reviews jika ada
try:
    more_reviews = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ulasan lainnya') or contains(text(), 'More reviews')]/ancestor::button")))
    more_reviews.click()
    print("[INFO] Klik tombol More reviews.")
    time.sleep(3)
except:
    print("[INFO] Tidak ada tombol More reviews.")

# Loop berdasarkan elemen container
data_reviews = []
seen_reviews = set()
data_value = 500
first_scroll_attempt = 0
last_scroll_attempt = 200
print('Mulai scroll')

while first_scroll_attempt < last_scroll_attempt and len(data_reviews) < data_value:
    # cari element container
    reviews_container = driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf')
    for container in reviews_container:
        try:
            username = container.find_element(By.CLASS_NAME, 'd4r55').text.strip()
        except:
            username = 'Unknown'

        try:
            review = container.find_element(By.CLASS_NAME, 'wiI7pd').text.strip()
        except:
            review = ''

        try:
            rating_el = container.find_element(By.CLASS_NAME, 'kvMYJc')
            rating = rating_el.get_attribute('aria-label').split()[0]
        except:
            rating = 'Unknown'
        
        # Klik tombol tombol lainnya di dalam review jika ada
        try:
            more_button = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "Lihat lainnya")]')
            for more in more_button:
                try:
                    driver.execute_script('arguments[0].click();', more)
                    print('[INFO] tombol lainnya di klik')
                    time.sleep(0.3)
                except Exception as e:
                    print(f'[INFO] tombol lainnya gagal di klik: {e}')
        except:
            print('[INFO] tidak ada tombol lainnya')
        
        # Cek duplikasi
        unique_key = (username, review)
        if review and unique_key not in data_reviews:
            seen_reviews.add(unique_key)
            data_reviews.append({
                'username': username, 'review': review, 'rating': rating
            })

    # Scroll berdasarkan element terakhir
    if reviews_container:
        driver.execute_script('arguments[0].scrollIntoView();', reviews_container[-1])
    else:
        print('Tidak bisa scroll')
        pass
    
    print(f'[INFO] data ulasan terkumpul: {len(data_reviews)}')
    time.sleep(2)
    first_scroll_attempt += 1

    if len(data_reviews) >= data_value:
        print(f"[INFO] Data sudah mencapai {len(data_reviews)} ulasan, berhenti scrolling.")
        break
    
# Tampilkan hasil
for i, data in enumerate(data_reviews[:data_value], 1):
    print(f'{i}. {data['username']}')
    print(f'{data['rating']}')
    print(f'{data['review']}\n')

# Simpan ke CSV
df = pd.DataFrame(data_reviews)
df.to_csv('ulasan_graha_persib.csv', index=False)
print('[INFO] data berhasil disimpan ke ulasan_graha_persib.csv')
driver.quit()