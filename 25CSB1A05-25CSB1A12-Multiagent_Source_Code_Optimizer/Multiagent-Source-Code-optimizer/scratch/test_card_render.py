from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:5173')
    time.sleep(2)
    with open('scratch/vulnerable_samples.cpp', 'r', encoding='utf-8') as f:
        cpp_code = f.read()

    driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
    driver.execute_script('window.__COMPILER_AI__.setLanguage("cpp")')
    driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', cpp_code)
    time.sleep(0.5)
    driver.execute_script('window.__COMPILER_AI__.startRun()')

    for _ in range(40):
        time.sleep(0.5)
        st = driver.execute_script('return window.__COMPILER_AI__.getState()')
        if st and st.get('status') == 'completed':
            break

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
    time.sleep(1)
    
    # Target only finding cards inside the findings list container
    cards = driver.find_elements('css selector', 'div.space-y-3 > div.rounded-xl')
    print('Filtered Security cards:', len(cards))
    if cards:
        cards[0].screenshot('scratch/sample_card_0.png')
        print('Card 0 text:', cards[0].text[:120].replace('\n', ' -- '))
        im = Image.open('scratch/sample_card_0.png')
        print('Card 0 image size:', im.size)
        if len(cards) > 1:
            print('Card 1 text:', cards[1].text[:120].replace('\n', ' -- '))
finally:
    driver.quit()
