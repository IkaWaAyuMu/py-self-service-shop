from django.shortcuts import render, redirect
from django.conf import settings
from django import forms
from django.http import HttpResponseRedirect
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image,ImageDraw
import time
# Create your views here.
from django.http import HttpResponse
import paho.mqtt.client as mqtt
from website.models import Product
from decouple import config
import pyautogui

from crc import Configuration, Calculator, Crc16
from qr_code.qrcode.utils import QRCodeOptions

total_money = 0.0
product_list = []

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
    
def home_view(request, id):
    qrcode_img = qrcode.make((qr_code(account="0882807134",one_time=True,money="50")))
    img_name = 'qrcode.png'
    qrcode_img.save(str(settings.MEDIA_ROOT) + '/' + img_name)
    return render(request, 'home.html',{'img_name' : img_name})

class AddProductForm(forms.Form):
    ProductName = forms.CharField(label="Product name")
    SerialNo = forms.CharField(label="Serial Number (Code)")
    Price = forms.FloatField(label="Price (in Baht)")

def add_view(request, id):

    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if (form.is_valid()):
            print(form.cleaned_data['ProductName'] + form.cleaned_data['SerialNo'] + str(form.cleaned_data['Price']))
            if (Product.objects.create(product_name=form.cleaned_data['ProductName'] ,product_quanity=999 ,product_price= form.cleaned_data['Price'] ,product_serial_num=form.cleaned_data['SerialNo'])):
                return redirect('/addProduct/{}'.format(id)) 
    else:
        form = AddProductForm()
        return render(request, "addProduct.html", {'form': form, 'url': '/addProduct/{}'.format(id)})

def on_connect(mqtt_client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe('scanner/0')
   else:
       print('Bad connection. Code:', rc)

def on_message(mqtt_client, userdata, msg):
    global total_money
    global product_list
    # Product.objects.create(product_name="Test2",product_quanity=10,product_price=10,product_serial_num=msg.payload.decode("UTF-8"))
    if(msg.payload.decode("UTF-8") == "RESET"):
        total_money = 0.0
        product_list = []
    if(msg.payload.decode("UTF-8") == "CONFIRM"):
        total_money = 0.0
        for i in range(len(product_list)):
            update = Product.objects.get(product_serial_num=product_list[i].product_serial_num)
            update.product_quanity -= 1
            print(update.product_quanity)
            update.save()
        product_list = []
    try:
        print(Product.objects.get(product_serial_num=msg.payload.decode("UTF-8")).product_price)
        total_money+=Product.objects.get(product_serial_num=msg.payload.decode("UTF-8")).product_price
        product_list.append(Product.objects.get(product_serial_num=msg.payload.decode("UTF-8")))
    finally:
        print(total_money)
        for i in range(len(product_list)):
            print(product_list[i])
            print(product_list[i].product_serial_num)
        
        print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
        pyautogui.hotkey('f5')
        return HttpResponseRedirect('/')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(config("MQTT_USER"), config("MQTT_PASSWORD"))
client.connect(
    host=config("MQTT_SERVER"),
    port=int(config("MQTT_PORT")),
    keepalive=int(config("MQTT_KEEPALIVE"))
)

client.loop_start()