import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def capture_graphs():
    # Setup directories
    workspace = "d:\\ex_work\\AirQualityReview_Project"
    screenshot_dir = os.path.join(workspace, "validation_docs", "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Brain artifacts directory
    brain_dir = r"C:\Users\thana\.gemini\antigravity\brain\aa85b059-14a1-4288-a587-0cefeb8d2e06"
    
    print(f"Screenshots will be saved in: {screenshot_dir}")
    
    # Configure Edge options in headless mode
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1600")
    
    driver = webdriver.Edge(options=options)
    driver.set_window_size(1920, 1600)
    
    try:
        # Navigate to Dashboard
        print("Navigating to Dashboard...")
        driver.get("http://127.0.0.1:5000/aqr")
        time.sleep(3)
        
        # Inject paths
        print("Injecting folder paths...")
        folder_input = driver.find_element(By.ID, "folderPath")
        limit_input = driver.find_element(By.ID, "setpointPath")
        
        raw_folder_path = os.path.join(workspace, "data", "C")
        limit_file_path = os.path.join(workspace, "data", "SetPointLimit.xlsx")
        
        driver.execute_script("arguments[0].value = arguments[1]", folder_input, raw_folder_path)
        driver.execute_script("arguments[0].value = arguments[1]", limit_input, limit_file_path)
        
        # Trigger checkReadyForScan to populate dates and let the app scan files properly
        print("Triggering checkReadyForScan()...")
        driver.execute_script("checkReadyForScan();")
        
        # Wait until dates are populated (which signals that get-file-info was successful)
        print("Waiting for temporal range fields to populate...")
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.ID, "startDate").get_attribute("value") != ""
        )
        print(f"Dates populated: Start={driver.find_element(By.ID, 'startDate').get_attribute('value')}, End={driver.find_element(By.ID, 'endDate').get_attribute('value')}")
        time.sleep(1)
        
        # Click Scan & Load Rooms
        print("Clicking Scan & Load Available Rooms...")
        load_rooms_btn = driver.find_element(By.ID, "loadRoomsBtn")
        driver.execute_script("arguments[0].click();", load_rooms_btn)
        
        # Wait for Room list card to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "roomSelectionSection"))
        )
        time.sleep(2)
        
        # Select 3 specific rooms with violation data programmatically to ensure curves are drawn immediately
        print("Selecting specific rooms...")
        driver.execute_script("""
            selectedRooms.clear();
            selectedRooms.add('1-P047');
            selectedRooms.add('M5 2-P156');
            selectedRooms.add('M5 2-P168');
            renderAvailableRooms();
            renderSelectedRooms();
        """)
        time.sleep(1)
        
        # Scroll down to analyze button and trigger analysis
        analyze_btn = driver.find_element(By.ID, "analyzeBtn")
        driver.execute_script("arguments[0].scrollIntoView();", analyze_btn)
        time.sleep(0.5)
        
        print("Starting analysis...")
        driver.execute_script("arguments[0].click();", analyze_btn)
        
        # Wait for plotBtn to be enabled (indicates analysis is complete and currentJobId is set)
        print("Waiting for analysis to complete (plotBtn to be enabled)...")
        WebDriverWait(driver, 120).until(
            lambda d: d.execute_script("return !document.getElementById('plotBtn').disabled;")
        )
        time.sleep(2)
        
        # Click PlotBtn
        print("Generating Visual Graphs...")
        plot_btn = driver.find_element(By.ID, "plotBtn")
        driver.execute_script("arguments[0].click();", plot_btn)
        
        # Wait for Plotly charts to render
        print("Waiting for graphs to render...")
        time.sleep(15)
        
        # Ensure scroll container allows finding elements properly
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Helper to take screenshot robustly
        def capture_element_robustly(xpath_query, filename):
            try:
                el = driver.find_element(By.XPATH, xpath_query)
                rect = driver.execute_script("return arguments[0].getBoundingClientRect();", el)
                print(f"Element {filename} dimensions: {rect}")
                
                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                time.sleep(1.5)
                
                output_path = os.path.join(screenshot_dir, filename)
                
                # Attempt element screenshot
                try:
                    el.screenshot(output_path)
                    print(f"Successfully saved element screenshot to: {output_path}")
                except Exception as ex_el:
                    print(f"Element screenshot failed for {filename}: {ex_el}. Trying viewport fallback.")
                    # Viewport fallback
                    driver.save_screenshot(output_path)
                    print(f"Saved viewport fallback screenshot to: {output_path}")
                    
            except Exception as e:
                print(f"Failed to locate or screenshot element for {filename}: {e}")

        # 1. Capture Heatmap Card
        print("Capturing Heatmap Card...")
        capture_element_robustly('//div[@id="violationHeatmap"]/ancestor::div[contains(@class, "card")][1]', "06_a_heatmap.png")
        
        # 2. Capture Timeline Card
        print("Capturing Timeline Card...")
        capture_element_robustly('//div[@id="violationTimelineChart"]/ancestor::div[contains(@class, "card")][1]', "06_b_timeline.png")
        
        # 3. Capture Summary (Overview Bar Chart) Card
        print("Capturing Overview Card...")
        capture_element_robustly('//div[@id="summaryViolationChart"]/ancestor::div[contains(@class, "card")][1]', "06_c_bar_chart.png")
        
        # 4. Capture Statistical Table Card
        print("Capturing Statistical Table Card...")
        capture_element_robustly('//tbody[@id="summaryTableBody"]/ancestor::div[contains(@class, "card")][1]', "06_d_violation_table.png")
        
        # 5. Capture Time-Series Plots Stack
        print("Capturing Time-Series Plots Stack...")
        capture_element_robustly('//div[contains(@class, "plots-stack")]', "06_e_time_series.png")
        
        # Print browser logs to help diagnose any JS errors
        print("\n--- BROWSER CONSOLE LOGS ---")
        for entry in driver.get_log('browser'):
            print(entry)
        print("----------------------------\n")
        
        # Copy files to brain directory
        if os.path.exists(brain_dir):
            print("Copying captured images to brain directory...")
            for filename in ["06_a_heatmap.png", "06_b_timeline.png", "06_c_bar_chart.png", "06_d_violation_table.png", "06_e_time_series.png"]:
                src = os.path.join(screenshot_dir, filename)
                dst = os.path.join(brain_dir, filename)
                shutil.copy(src, dst)
                print(f"Copied {filename} to brain directory.")
        
        print("All individual graphs captured successfully!")
        
    except Exception as e:
        print(f"Error during graph capture: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_graphs()
