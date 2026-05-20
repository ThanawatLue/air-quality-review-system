import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_screenshot_pipeline():
    # Setup directories
    workspace = "d:\\ex_work\\AirQualityReview_Project"
    screenshot_dir = os.path.join(workspace, "validation_docs", "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print(f"Screenshots will be saved in: {screenshot_dir}")
    
    # Configure Edge options in headless mode
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1600,1200")
    
    driver = webdriver.Edge(options=options)
    driver.set_window_size(1600, 1200)
    
    try:
        # =====================================================================
        # STAGE 1: Initial Dashboard Page Load
        # =====================================================================
        print("Navigating to Dashboard...")
        driver.get("http://127.0.0.1:5000/aqr")
        time.sleep(2)
        
        initial_path = os.path.join(screenshot_dir, "01_dashboard_initial.png")
        driver.save_screenshot(initial_path)
        print(f"Captured: {initial_path}")
        
        # =====================================================================
        # STAGE 2: Fill Configuration Paths
        # =====================================================================
        print("Filling folder paths...")
        folder_input = driver.find_element(By.ID, "folderPath")
        limit_input = driver.find_element(By.ID, "setpointPath")
        
        # Paths to inject
        raw_folder_path = os.path.join(workspace, "data", "C")
        limit_file_path = os.path.join(workspace, "data", "SetPointLimit.xlsx")
        
        # Inject values directly using Javascript since the inputs are read-only
        driver.execute_script("arguments[0].value = arguments[1]", folder_input, raw_folder_path)
        driver.execute_script("arguments[0].value = arguments[1]", limit_input, limit_file_path)
        
        # Trigger the change events or AI badges to update by simulating scan triggers
        # In our script.js, showing the Step 2 Card is triggered after paths are not empty
        driver.execute_script("document.getElementById('sidebarDateTime').style.display = 'block';")
        time.sleep(1)
        
        filled_path = os.path.join(screenshot_dir, "02_dashboard_filled.png")
        driver.save_screenshot(filled_path)
        print(f"Captured: {filled_path}")
        
        # =====================================================================
        # STAGE 3: Scan & Load Rooms
        # =====================================================================
        print("Clicking Scan & Load Available Rooms...")
        load_rooms_btn = driver.find_element(By.ID, "loadRoomsBtn")
        # Direct JS click to bypass overlap issues if any
        driver.execute_script("arguments[0].click();", load_rooms_btn)
        
        # Wait for Room list card to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_type_located
            if hasattr(EC, "visibility_of_element_type_located") else 
            EC.presence_of_element_located((By.ID, "roomSelectionSection"))
        )
        time.sleep(2) # Give a second for anims
        
        rooms_loaded_path = os.path.join(screenshot_dir, "03_dashboard_rooms_loaded.png")
        driver.save_screenshot(rooms_loaded_path)
        print(f"Captured: {rooms_loaded_path}")
        
        # =====================================================================
        # STAGE 4: Select All Rooms and Trigger Review Analysis
        # =====================================================================
        print("Selecting all rooms and starting analysis...")
        
        # Click Select All Areas and Select All Available Rooms
        area_all_btn = driver.find_element(By.ID, "areaSelectAllBtn")
        avail_all_btn = driver.find_element(By.ID, "availSelectAllBtn")
        driver.execute_script("arguments[0].click();", area_all_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", avail_all_btn)
        time.sleep(0.5)
        
        # Scroll down to analyze button
        analyze_btn = driver.find_element(By.ID, "analyzeBtn")
        driver.execute_script("arguments[0].scrollIntoView();", analyze_btn)
        time.sleep(0.5)
        
        print("Clicking Generate Summary Reports...")
        driver.execute_script("arguments[0].click();", analyze_btn)
        
        # Wait for terminal to show the analysis logs
        time.sleep(5) # Let it run and display terminal output
        
        analysis_path = os.path.join(screenshot_dir, "04_analysis_executing.png")
        driver.save_screenshot(analysis_path)
        print(f"Captured: {analysis_path}")
        
        # Wait for analysis to complete by checking that plotBtn is enabled
        print("Waiting for analysis to complete (plotBtn to be enabled)...")
        WebDriverWait(driver, 120).until(
            lambda d: d.execute_script("return !document.getElementById('plotBtn').disabled;")
        )
        time.sleep(2)
        
        analysis_done_path = os.path.join(screenshot_dir, "05_analysis_completed.png")
        driver.save_screenshot(analysis_done_path)
        print(f"Captured: {analysis_done_path}")
        
        # =====================================================================
        # STAGE 5: Generate Visual Graphs
        # =====================================================================
        print("Generating Visual Graphs...")
        plot_btn = driver.find_element(By.ID, "plotBtn")
        driver.execute_script("arguments[0].click();", plot_btn)
        
        # Wait for graphs container to load Plotly charts
        time.sleep(15)
        
        # Scroll to visual graphs
        graphs_container = driver.find_element(By.ID, "graphResults")
        driver.execute_script("arguments[0].scrollIntoView();", graphs_container)
        time.sleep(1)
        
        graphs_path = os.path.join(screenshot_dir, "06_dashboard_visual_graphs.png")
        driver.save_screenshot(graphs_path)
        print(f"Captured: {graphs_path}")
        
        # =====================================================================
        # STAGE 6: Data Transformation Page Load
        # =====================================================================
        print("Navigating to Data Transformation Module...")
        driver.get("http://127.0.0.1:5000/transform")
        time.sleep(2)
        
        transform_initial_path = os.path.join(screenshot_dir, "07_transform_initial.png")
        driver.save_screenshot(transform_initial_path)
        print(f"Captured: {transform_initial_path}")
        
        # =====================================================================
        # STAGE 7: Fill Data Transformation Inputs
        # =====================================================================
        print("Filling Data Transformation paths...")
        rmt_input = driver.find_element(By.ID, "rmtPath")
        rmh_input = driver.find_element(By.ID, "rmhPath")
        rpt_input = driver.find_element(By.ID, "rptPath")
        out_input = driver.find_element(By.ID, "outputDir")
        
        # Paths to inject
        rmt_path = os.path.join(workspace, "data", "RMT(TEMP M1-2-P1-WH-3-4-P2).csv")
        rmh_path = os.path.join(workspace, "data", "RMH(HUM M1-2-P1-WH-3-4-P2).csv")
        rpt_path = os.path.join(workspace, "data", "RPT(PRESSURE M1-2-P1-WH-3-4-P2).csv")
        out_path = os.path.join(workspace, "data", "C")
        
        # Inject paths
        driver.execute_script("arguments[0].value = arguments[1]", rmt_input, rmt_path)
        driver.execute_script("arguments[0].value = arguments[1]", rmh_input, rmh_path)
        driver.execute_script("arguments[0].value = arguments[1]", rpt_input, rpt_path)
        driver.execute_script("arguments[0].value = arguments[1]", out_input, out_path)
        time.sleep(1)
        
        transform_filled_path = os.path.join(screenshot_dir, "08_transform_filled.png")
        driver.save_screenshot(transform_filled_path)
        print(f"Captured: {transform_filled_path}")
        
        # =====================================================================
        # STAGE 8: Execute Transformation
        # =====================================================================
        print("Executing split and transform...")
        transform_btn = driver.find_element(By.ID, "transformBtn")
        driver.execute_script("arguments[0].click();", transform_btn)
        
        # Wait for processing log to show completion (e.g. check loading overlay disappearance)
        time.sleep(10) # Transformation runs quickly
        
        transform_complete_path = os.path.join(screenshot_dir, "09_transform_completed.png")
        driver.save_screenshot(transform_complete_path)
        print(f"Captured: {transform_complete_path}")
        
        print("All screenshots captured successfully!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_screenshot_pipeline()
