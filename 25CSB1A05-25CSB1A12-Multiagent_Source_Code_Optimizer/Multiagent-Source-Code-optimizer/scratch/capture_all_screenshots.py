"""
Automated Selenium script to run benchmark inputs on http://localhost:5173 and capture
crisp screenshots (.1 through .17) for the research paper test cases section.
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_automation():
    os.makedirs('scratch/screenshots', exist_ok=True)

    # 1. Read input codes
    with open('scratch/vulnerable_samples.cpp', 'r', encoding='utf-8') as f:
        cpp_code = f.read()

    with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
        py_code = f.read()

    # 2. Configure Chrome
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    print("Browser started.")

    try:
        driver.get('http://localhost:5173')
        time.sleep(3)

        # Helper to wait for run completion
        def wait_for_run(timeout_s=30):
            t0 = time.time()
            while time.time() - t0 < timeout_s:
                state = driver.execute_script('return window.__COMPILER_AI__ ? window.__COMPILER_AI__.getState() : null')
                if state and state.get('status') in ('completed', 'failed', 'partially_completed'):
                    return state
                time.sleep(0.4)
            return None

        # Helper to set results panel height so tabs are well displayed
        def expand_results(height=480):
            driver.execute_script(f'window.__COMPILER_AI__.setResultsHeight({height})')
            time.sleep(0.5)

        # -------------------------------------------------------------
        # SUITE 1: C++ Benchmark (vulnerable_samples.cpp) in Full Pipeline Mode
        # -------------------------------------------------------------
        print("Executing Suite 1: C++ Benchmark...")
        driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("cpp")')
        driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', cpp_code)
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')

        res = wait_for_run(20)
        print("C++ Run status:", res.get('status') if res else 'timeout')
        expand_results(450)

        # Screenshot .1: Overview with Output Tab
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("output")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_1.png')
        print("Captured Screenshot .1 (C++ Pipeline Overview & Output Tab)")

        # Screenshot .2: Optimized Code Tab (Side-by-side diff + 21 applied transformations)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_2.png')
        print("Captured Screenshot .2 (C++ Optimized Code & Transformations)")

        # Screenshot .3: Security Tab - Top Section (Buffer Overflows & Format Strings)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
        time.sleep(1)
        # Scroll security panel to top
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 0;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_3.png')
        print("Captured Screenshot .3 (C++ Security Findings - Section 1)")

        # Screenshot .4: Security Tab - Mid Section (Memory Management & Injection)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 900;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_4.png')
        print("Captured Screenshot .4 (C++ Security Findings - Section 2)")

        # Screenshot .5: Security Tab - Lower Section (Crypto, Secrets, OOP Flaws)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 1800;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_5.png')
        print("Captured Screenshot .5 (C++ Security Findings - Section 3)")

        # Screenshot .6: Messages Tab (Execution trace stream)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("messages")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_6.png')
        print("Captured Screenshot .6 (C++ Lifecycle Event Stream)")

        # -------------------------------------------------------------
        # SUITE 2: Python Benchmark (vulnerable_samples.py) in Full Pipeline Mode
        # -------------------------------------------------------------
        print("\nExecuting Suite 2: Python Benchmark...")
        driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("python")')
        driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', py_code)
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')

        res_py = wait_for_run(20)
        print("Python Run status:", res_py.get('status') if res_py else 'timeout')
        expand_results(450)

        # Screenshot .7: Overview with Output Tab
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("output")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_7.png')
        print("Captured Screenshot .7 (Python Pipeline Overview & Output Tab)")

        # Screenshot .8: Optimized Code Tab (Side-by-side diff + 34 transformations)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_8.png')
        print("Captured Screenshot .8 (Python Optimized Code & Transformations)")

        # Screenshot .9: Security Tab - Section 1 (SQL Injection, OS Command, Code/Eval)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
        time.sleep(1)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 0;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_9.png')
        print("Captured Screenshot .9 (Python Security Findings - Section 1)")

        # Screenshot .10: Security Tab - Section 2 (Other Injections, Deserialization)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 850;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_10.png')
        print("Captured Screenshot .10 (Python Security Findings - Section 2)")

        # Screenshot .11: Security Tab - Section 3 (Path Traversal, Permissions, Secrets)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 1750;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_11.png')
        print("Captured Screenshot .11 (Python Security Findings - Section 3)")

        # Screenshot .12: Security Tab - Section 4 (Network, CSRF/SSRF, Logic Flaws)
        driver.execute_script('''
            const sec = document.querySelector('.overflow-y-auto');
            if (sec) sec.scrollTop = 2650;
        ''')
        time.sleep(0.5)
        driver.save_screenshot('scratch/screenshots/screenshot_12.png')
        print("Captured Screenshot .12 (Python Security Findings - Section 4)")

        # Screenshot .13: Messages Tab (Python lifecycle trace stream)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("messages")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_13.png')
        print("Captured Screenshot .13 (Python Lifecycle Event Stream)")

        # -------------------------------------------------------------
        # SUITE 3: Dedicated Modes & Built-in Starters
        # -------------------------------------------------------------
        # Screenshot .14: C++ Built-in Starter Sample in Dedicated Optimize Mode
        print("\nExecuting Suite 3: C++ Optimize Mode...")
        driver.execute_script('window.__COMPILER_AI__.setMode("optimize")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("cpp")')
        # Trigger default starter reload or run
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')
        wait_for_run(15)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_14.png')
        print("Captured Screenshot .14 (C++ Starter in Dedicated Optimize Mode)")

        # Screenshot .15: Python Built-in Starter Sample in Dedicated Security Mode
        print("Executing Suite 3: Python Security Mode...")
        driver.execute_script('window.__COMPILER_AI__.setMode("security")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("python")')
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')
        wait_for_run(15)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_15.png')
        print("Captured Screenshot .15 (Python Starter in Dedicated Security Mode)")

        # Screenshot .16: C Language Built-in Starter Sample in Full Pipeline Mode
        print("Executing Suite 3: C Language Pipeline Mode...")
        driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("c")')
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')
        wait_for_run(15)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("output")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_16.png')
        print("Captured Screenshot .16 (C Language Starter in Full Pipeline Mode)")

        # Screenshot .17: JavaScript Built-in Starter Sample in Full Pipeline Mode
        print("Executing Suite 3: JavaScript Language Pipeline Mode...")
        driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
        driver.execute_script('window.__COMPILER_AI__.setLanguage("javascript")')
        time.sleep(1)
        driver.execute_script('window.__COMPILER_AI__.startRun()')
        wait_for_run(15)
        driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
        time.sleep(1)
        driver.save_screenshot('scratch/screenshots/screenshot_17.png')
        print("Captured Screenshot .17 (JavaScript Starter in Full Pipeline Mode)")

        print("\nALL 17 SCREENSHOTS CAPTURED SUCCESSFULLY!")

    finally:
        driver.quit()

if __name__ == '__main__':
    run_automation()
