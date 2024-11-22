# Import necessary libraries/modules
import csv
import os
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import custom module/s
import utils

# Declaring constants
BASEURL = "https://www.linkedin.com/login"
CHROMEDRIVERFILEPATH = r".\chromedriver.exe"
EMPLOYEEFILECOLS = ['Name', 'ConnectionDegree','Description','Location',
                   'LinkedIN_URL', 'OtherDetails']

if __name__ == "__main__":
    try:
        # load LinkedIN login credentials as environment variables
        if not load_dotenv(".env"):
            raise utils.MyError("No LinkedIn login credential file found")

        # Get user input on organisation's LinkedIN url
        entityurl = input(
            """Please input the LinkedIN url for the organisation of interest.\n
        For example,the LinkedIN url for CCCS is
            https://www.linkedin.com/company/cccs-sg \n: """
            )

        # Initialise Chrome driver and navigate to LinkedIN log in page
        driver = utils.initialise_driver(CHROMEDRIVERFILEPATH)
        driver.get(BASEURL)
        # Input username
        username = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "username"))
        )
        username.send_keys(os.getenv("USER"))
        # Input password
        password = driver.find_element(By.ID, "password")
        password.send_keys(os.getenv("PASSWRD"))
        # Click on the Sign in button
        signin = driver.find_element(By.CLASS_NAME, "btn__primary--large")
        signin.click()

        # Navigate to the LinkedIN homepage for the organisation of interest
        driver.get(entityurl)

        # Get organisation name
        orgname = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((
            By.CLASS_NAME, "org-top-card-summary__title"))).text.replace(' ', '_')

        # Access the base url for its lists of employees
        employeebaseurl = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((
            By.CLASS_NAME, "org-top-card-summary-info-list__info-item-link")))\
            .get_attribute("href")

        # Initialise the employee info file, if it has yet to exist
        employeefilepath = f".\{orgname}_{datetime.now().date().strftime('%d%b%Y')}.csv"
        if not os.path.exists(employeefilepath):
            with open(employeefilepath, 'w', newline='') as f:
                file = csv.writer(f)
                file.writerow(EMPLOYEEFILECOLS)

        # Extract employee details page by page and save in employee info file
        # Open up the employee info file
        with open(employeefilepath, 'a', newline='', encoding='utf-8') as f1:
            employee_append = csv.writer(f1)

            # iterate through the pages
            for pgnum in range(100):
                driver.get(employeebaseurl + "&page=" + str(pgnum+1))
                # extract employee details as long as employee results are available
                try:
                                        
                    details = WebDriverWait(driver, 5).until(
                                EC.visibility_of_all_elements_located((
                                    By.XPATH, "//div[@class='entity-result__universal-image']/following-sibling::div[1]")))
                    
                    employees, names, connection, description, location, otherdetails, url = ([] for i in range(7))
                    
                    for ele in details:
                        try:
                            employees.append(ele.find_element(By.CLASS_NAME, "entity-result__title-line").text)
                        except NoSuchElementException:
                            employees.append('')
                        # extract the headline published by employee, if any
                        try:
                            description.append(ele.find_element(By.CLASS_NAME, "entity-result__primary-subtitle").text)
                        except NoSuchElementException:
                            description.append('')
                        # extract the location published by employee, if any
                        try:
                            location.append(ele.find_element(By.CLASS_NAME, "entity-result__secondary-subtitle").text)
                        except NoSuchElementException:
                            location.append('')
                        # extract the shared connections, if any
                        try:
                            otherdetails.append(ele.find_element(By.CLASS_NAME, "entity-result__insights").text)
                        except NoSuchElementException:
                            otherdetails.append('')
                        # extract the LinkedIN url of employee, if any
                        try:
                            url.append(ele.find_element(By.CLASS_NAME, "app-aware-link ").get_attribute('href'))
                        except NoSuchElementException:
                            url.append('')
                    # extract the names of employees
                    names = [ele.split('\n')[0] for ele in employees]
                    # extract the degree connection of employees
                    connection = [''.join(re.findall(r'(\d\S+ degree connection)', ele)) for ele in employees]
                    # writing employees detailed extracted from page to csv file
                    for i in range(len(names)):
                        employee_append.writerow([names[i], connection[i], description[i],
                                                  location[i], url[i], otherdetails[i]]) 
                        
                except TimeoutException:
                    print("The scrapper should have reached the end of the employee list, please double check.")
                    break
                
                print(f"Employee details extracted from page {str(pgnum+1)}")
            
    except TimeoutException:
        raise utils.MyError(
                "5 sec time out trying to wait for element to be visible, \
                please troubleshoot the relevant elements")
        
    except NoSuchElementException as e:
        raise utils.MyError(
                "Unable to locate element. See error msg for \
                 affected element(s).\n" + str(e))
                 
    except (utils.MyError, Exception, BaseException) as e:
        raise utils.MyError(str(e))
        
    finally:
        # Close the browser regardless whether scraping is successful
        driver.quit()
