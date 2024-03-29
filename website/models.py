from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image,ImageDraw
# Create your models here.
class Website(models.Model):
    name = models.CharField(max_length=200)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)

    def __str__(self):
        return str(self.name)
    
    def save(self,*args,**kwargs):
        qrcode_img = qrcode.make(self.name)
        canvas = Image.new('RGB', (qrcode_img.pixel_size, qrcode_img.pixel_size), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname =f'qr_code-{self.name}.png'
        buffer = BytesIO()
        canvas.save(buffer,'PNG')
        self.qr_code.save(fname,File(buffer),save=False)
        canvas.close()
        super().save(args,kwargs)

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_quanity = models.IntegerField()
    product_price = models.FloatField()
    product_serial_num = models.CharField(max_length=1000)
    def __str__(self):
        return str(self.product_name)