from django.shortcuts import render
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image,ImageDraw
import time
# Create your views here.
from django.http import HttpResponse
from website.models import Product

from crc import Configuration, Calculator, Crc16
from qr_code.qrcode.utils import QRCodeOptions



def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1


def qr_code(account,one_time=True,path_qr_code="",country="TH",money="",currency="THB"):
    """
    qr_code(account,one_time=True,path_qr_code="",country="TH",money="",currency="THB")
    account is phone number or  identification number.
    one_time : if you use once than it's True.
    path_qr_code : path save qr code.
    country : TH
    money : money (if have)
    currency : THB
    """
    Version = "0002"+"01" # เวชั่นของ  PromptPay
    if one_time == True: # one_time คือ ต้องการให้โค้ดนี้ครั้งเดียวหรือไม่
        one_time = "010212" # 12 ใช้ครั้งเดียว
    else:
        one_time ="010211" # 11 ใช้ได้้หลายครั้ง
    
    if len(account) == 10 or len(account) == 13 : 
        merchant_account_information = "2937" # ข้อมูลผู้ขาย (เฉพาะเบอร์โทร และ บัตรประชาชน)
    else :
        merchant_account_information = "2939" # ข้อมูลผู้ขาย (เฉพาะเลขอ้างอิง)
        
    merchant_account_information += "0016"+"A000000677010111" # หมายเลขแอปพลิเคชั่น PromptPay
    if len(account) == 10: #ถ้าบัญชีนี้เป็นเบอร์โทร
        account = list(account)
        merchant_account_information += "011300" # 01 หมายเลขโทรศัพท์ ความยาว 13 ขึ้นต้น 00
        if country == "TH":
            merchant_account_information += "66" # รหัสประเทศ 66 คือประเทศไทย
        del account[0] # ตัดเลข 0 หน้าเบอร์ออก
        merchant_account_information += ''.join(account)
    elif len(account) == 13 : #ถ้าบัญชีนี้เป็นบัตรประชาชน
        merchant_account_information += "0213" + account.replace('-','')
    else : #ไม่ใช่เบอร์โทร และ บัตรประชาชน เป็นเลขอ้างอิง
        merchant_account_information += "0315" + account + "5303764"
    country = "5802" + country # ประเทศ
    if currency == "THB":
        currency = "5303" + "764" # "764"  คือเงินบาทไทย ตาม https://en.wikipedia.org/wiki/ISO_4217
    if money != "": # กรณีกำหนดเงิน
        check_money = money.split('.') # แยกจาก .
        if len(check_money) == 1 or len(check_money[1]) == 1: # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
            money = "54" + "0" + str(len(str(float(money))) + 1) + str(float(money)) + "0"
        else:
            money = "54" + "0" + str(len(str(float(money)))) + str(float(money)) # กรณีที่มีทศนิยมครบ
    check_sum = Version+one_time+merchant_account_information+country+currency+money+"6304" # เช็คค่า check sum
    # check_sum1 = hex(crc16.crc16xmodem(check_sum.encode('ascii'),0xffff)).replace('0x','')
    config = Configuration(
            width=16,
            polynomial=0x07,
            init_value=0xFFFF,
            final_xor_value=0x00,
            reverse_input=False,
            reverse_output=False,
        )
    check_sum1 = Calculator(config).checksum(bytes(check_sum.encode('ascii')))
    if len(str(check_sum1)) < 4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
        check_sum1 = ("0"*(4-len(str(check_sum1)))) + str(check_sum1)
    check_sum += str(check_sum1)
    if path_qr_code != "":
        img = qrcode.make(check_sum.upper())
        imgload = open(path_qr_code,'wb')
        img.save(imgload, 'PNG')
        imgload.close()
        return True
    else:
        return check_sum.upper() # upper ใช้คืนค่าสตริงเป็นตัวพิมพ์ใหญ่
    
def home_view(request):
    qrcode_img = qrcode.make((qr_code(account="0882807134",one_time=True,money="50")))
    img_name = 'qrcode.png'
    qrcode_img.save(str(settings.MEDIA_ROOT) + '/' + img_name)
    # obj = Website.objects.get(id=1)

    # context = {
    #     'name': name,
    #     'obj': obj,
    # }
    # return render(request, 'home.html',context)
    return render(request, 'home.html',{'img_name' : img_name})

Product.objects.create(product_name="Test",product_quanity=10,product_price=10,product_serial_num="12333")
# print(Product.objects.get(id=1))
# print(qr_code(account="0882807134",one_time=True,money="50"))