from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from font_intuitive import Intuitive
from inky import InkyPHAT_SSD1608
import qrcode
import time

class Display():
        def __init__(self):
                self.inky_display = InkyPHAT_SSD1608("black")
                self.inky_display.set_border(self.inky_display.WHITE)                

        def update_stream_display(self, device_id, thingsboard, vlt, dt, stream='http://192.168.0.10:8000'):
                # Setup epaper detail..
                epaper_resolution = 250,122
                img = Image.new(mode = 'P', size=(epaper_resolution[0], epaper_resolution[1]), color=1)
                draw = ImageDraw.Draw(img)
                # Create QR codes
                # WIFI.
                qr = qrcode.QRCode(version=1, box_size=2, border = 0)
                qr.add_data('WIFI:S:' + device_id + ';T:')
                wifi_qr = qr.make_image()
                img.paste(wifi_qr,(0,0))
                # Website.
                qr = qrcode.QRCode(version=1, box_size=2, border=0)
                qr.add_data(thingsboard)
                web_qr = qr.make_image()
                img.paste(web_qr,(200,0))
                # Stream.
                qr = qrcode.QRCode(version=1,box_size=2,border=0)
                qr.add_data(stream)
                stream_qr = qr.make_image()
                img.paste(stream_qr, (100,0))

                # Add labels
                fnt = ImageFont.truetype(FredokaOne,20)
                draw.text((3,90), device_id + dt, size=35, colour='black', font=fnt)
                draw.text((3,50), "WiFi", size=25, colour='black', font=fnt)
                draw.text((200,50),"Data", size=25, colour='black', font=fnt)
                draw.text((85,50),"Stream", size=25, colour='black', font=fnt)
                time.sleep(1)

                # Save image and load - a workaround to get the formatting working
                img.save('epapr.png')
                
                # Now write the updated to the display
                self.inky_display.set_image(epapr)
                self.inky_display.show()

        def update_acquisition_display(self, device_id, thingsboard, vlt, dt):
                # Setup epaper detail..
                epaper_resolution = 250,122
                img = Image.new(mode = 'P', size=(epaper_resolution[0], epaper_resolution[1]), color=1)
                draw = ImageDraw.Draw(img)
                # Create QR codes
                # Website.
                qr = qrcode.QRCode(version=1, box_size=2, border=0)
                qr.add_data('https://thingsboard.cloud/dashboard/3177a380-f956-11eb-ab24-1f8899a6f9b3?publicId=b43c0c50-4de0-11ec-ba3e-053b10063941')
                web_qr = qr.make_image()
                img.paste(web_qr,(0,0))

                # Now write the updated to the display
                inky_display.set_image(epapr)
                inky_display.show()
                # Add labels
                fnt = ImageFont.truetype(FredokaOne,20)
                draw.text((3,90), device_id + dt, size=35, colour='black', font=fnt)
                draw.text((3,50),"Data", size=25, colour='black', font=fnt)
                draw.text((80,0),"Datetime:" + dt)
                dsk_spc = os.statvfs()[4]
                dsk_spc = dsk_spc/1000000
                draw.text((80,40),"Disk space: " + str(dsk_spc))
                draw.text((80,80),"Temperature: ", str(00))
                time.sleep(1)

                # Save image and load - a workaround to get the formatting working
                img.save('epapr.png')
                
        def update_display(self):     
                inky_display = InkyPHAT_SSD1608("black")
                inky_display.set_border(inky_display.WHITE)
                # Build image
                self.construct_image()
                # Update display
                epapr = Image.open('epapr.png')
                self.inky_display.set_image(epapr)
                self.inky_display.show()
