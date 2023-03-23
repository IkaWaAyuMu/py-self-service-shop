# from django.shortcuts import render
# from django.conf import settings
# from website.models import Website
# import qrcode
# from io import BytesIO
# from django.core.files import File
# from PIL import Image,ImageDraw
# from website.views import qr_code
# import time


# # def home_view(request):
# #     qrcode_img = qrcode.make(qr_code(qr_code(account="0882807134",one_time=True,money="60")))
# #     img_name = 'qr' + str(time.time()) + '.png'
# #     qrcode_img.save(settings.MEDIA_ROOT + '/' + img_name)
# #     # obj = Website.objects.get(id=1)

# #     # context = {
# #     #     'name': name,
# #     #     'obj': obj,
# #     # }
# #     # return render(request, 'home.html',context)
# #     return render(request, 'home.html',{'img_name' : img_name})