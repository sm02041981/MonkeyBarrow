#SM: 4th Sept 2026
# This is the backend program to handle thermal printing of labels for book items. 
# It uses ESC/POS commands to send data to a thermal printer. 
# The label includes the serial number, location, and rack code.

# For ESC/POS thermal printers
"""
from escpos.printer import Usb, Network, Serial  
# For barcode generation (if you want barcodes on labels)
import barcode
from barcode.writer import ImageWriter

# For handling in-memory images
import io


def _print_label(serial_number: str, location: str, rack_code: str,
                 connection_type: str = "usb",
                 usb_ids: tuple = (0x04b8, 0x0e15, 0),
                 network_ip: str = "192.168.1.100",
                 serial_port: str = "/dev/ttyUSB0"):
    Print a label using a thermal printer with auto-detection of connection type.
    connection_type: "usb", "network", or "serial"
   
    # Select printer based on connection type
    if connection_type == "usb":
        vendor_id, product_id, interface = usb_ids
        printer = Usb(vendor_id, product_id, interface)
    elif connection_type == "network":
        printer = Network(network_ip)
    elif connection_type == "serial":
        printer = Serial(devfile=serial_port)
    else:
        raise ValueError("Unsupported connection type. Use 'usb', 'network', or 'serial'.")

    # Prepare label text
    label_text = (
        f"Serial No.: {serial_number}\n"
        f"Location: {location}\n"
        f"Rack Code: {rack_code}\n"
    )

    # Print text
    printer.text("🖨️ Printing label...\n")
    printer.text(label_text)

    # Generate barcode for serial number
    ean = barcode.get('code128', serial_number, writer=ImageWriter())
    buffer = io.BytesIO()
    ean.write(buffer)

    # Print barcode image
    printer.image(buffer)

    # Cut paper
    printer.cut()
"""