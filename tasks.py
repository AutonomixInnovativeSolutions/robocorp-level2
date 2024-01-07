from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    fill_the_form()
    archive_receipts()


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.configure(
        slowmo=1000,
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """clicks on ok"""
    page = browser.page()
    page.click("button:text('OK')")

def download_csv_file():
    """
    download csv file
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def get_orders():
    """Read data from csv and fill in the order form"""
    download_csv_file()
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders


def fill_the_form():
    """Fills in the robo order details"""
    order = get_orders()
    for order in order:
        close_annoying_modal()
        page = browser.page()
        page.select_option("#head", order["Head"])
        page.check("#id-body-"+order["Body"])
        page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
        page.fill("#address", str(order["Address"]))
        page.click("button:text('Preview')")
        page.click("#order")
        while "Error" in page.content():
            page.click("#order")
        store_receipt_as_pdf(order["Order number"])
        screenshot_robot(order["Order number"])
        order_number= order["Order number"]
        embed_screenshot_to_receipt("output/screenshots/receipt"+order_number+".png","output/receipts/receipt"+order_number+".pdf",)
        page.click("#order-another")

def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, "output/receipts/receipt"+order_number+".pdf")
    
def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="output/screenshots/receipt"+order_number+".png")    

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot],pdf_file,True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('output/receipts', 'output/receipts.zip')