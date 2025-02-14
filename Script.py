import time as t
import datetime as dt
from playwright.sync_api import Playwright, sync_playwright, expect

#___________________________________________________________________#
# YOUR SETTINGS
your_email = "YOUREMAIL" # Obviously, CHECK MY CODE!!!! Get in the habit of doing so; I could simply be sending your information to someone else!
your_password = "YOURPASSWORD" # Obviously, CHECK MY CODE!!!! Get in the habit of doing so; I could simply be sending your information to someone else!

location = "LOCATION" # Make sure the location you want is the first option in the dropdown menu
party_size = "2"
date_of_date = "15" # Same Month Only

# Desired Time Range (PM) - Only works well on days with nearly no reservation options available
start_time = 4 
end_time = 10

#___________________________________________________________________#


times = [":00 PM", ":15 PM", ":30 PM", ":45 PM"] # For some reason " :XX PM" might show as a button on the same hour

# Generate times for the desired time range
for i in range(start_time, end_time):
    for m in ("00", 15, 30, 45):
        times.append(f"{i}:{m} PM")


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    context.grant_permissions(["geolocation"])
    page = context.new_page()
    page.goto("https://www.thecheesecakefactory.com/reservations/login")
    page.get_by_role("button", name="Allow All").click()
    page.get_by_role("textbox", name="Enter email address").click()
    page.get_by_role("textbox", name="Enter email address").fill(your_email)
    page.get_by_role("textbox", name="Enter password").click()
    page.get_by_role("textbox", name="Enter password").fill(your_password)
    page.get_by_role("button", name="Log In").click()
    page.locator("#ion-overlay-1").get_by_role("button", name="Close").click() #This may need to be commented out, depending on if Cheesecake factory is advertising something at the time
    page.get_by_label("navigation").get_by_role("link", name="Reservations").click()
    page.get_by_role("textbox", name="enter location address").click()
    page.get_by_role("textbox", name="enter location address").fill(location)
    page.locator("app-locations-flyout form").get_by_role("button").click()
    page.wait_for_timeout(3000)
    page.get_by_role("link", name="Make a Reservation").first.click()
    page.get_by_role("textbox", name="Choose a Date").click()
    page.get_by_role("button", name=date_of_date).click()
    page.locator("#reservation-form-time").select_option("4:00 PM")
    page.locator("#reservation-form-party-size").select_option(party_size)
    page.get_by_role("button", name="Find A Table").click()

    loop = True
    while loop:
        for time in times:
            t.sleep(.1)
            if page.get_by_role("button", name=time).count() == 1:
                page.get_by_role("button", name=time).click()
                page.get_by_role("button", name="Confirm").click()
                page.get_by_role("button", name="View My Reservation").click()
                loop = False
                print("Reservation made at", time)
            else: 
                continue
        # I know, this is not the best code. It will raise and final exception after making a reservation ;)
        print("No reservation available at ", dt.datetime.now().strftime("%I:%M %p"), " still Looking...")        
        t.sleep(60)
        page.reload()
        page.get_by_role("textbox", name="Choose a Date").click()
        page.get_by_role("button", name=date_of_date).click()
        page.locator("#reservation-form-time").select_option("4:00 PM")
        page.locator("#reservation-form-party-size").select_option(party_size)
        page.get_by_role("button", name="Find A Table").click()
        t.sleep(2)

    # ---------------------
    context.close()
    browser.close()




try:
    
    print("\nConnecting to the big cheese...\n")
    with sync_playwright() as playwright:
        run(playwright)

except Exception as e:

    # Sometimes Playwright will give an error when a reservation pops up. This reconnects to grab the reservation.
    print(f"Error encountered: {e}. Restarting process in 5 seconds...")
    t.sleep(5)
    with sync_playwright() as playwright:
        run(playwright)


