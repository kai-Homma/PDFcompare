# -*- coding: utf-8 -*-
# """
# Created on Thu Jan  4 13:52:26 2024

# cd C:\Users\HOMMA.KAI.P\Desktop\python\PDFdiff
# streamlit run PDFeditor_web.py

# @author: HOMMA.KAI
# """

import streamlit as st

# import os
# import glob
# from pathlib import Path
# from pdf2image import convert_from_path
from pdf2image import convert_from_bytes
from PIL import Image
import numpy as np
import img2pdf
from io import BytesIO
# import tempfile
# import sys


def main():
    st.title("PDF比較")
    st.header('旧ファイル')
    old_file = st.file_uploader("変更前のファイルを入れて下さい", type="pdf", key="1234")
    st.header('新ファイル')
    new_file = st.file_uploader("変更後のファイルを入れて下さい", type="pdf", key="0000")
        
    if old_file is not None:
        if new_file is not None:            
            # oldimage = convert_pdf_to_images(old_file)
            # newimage = convert_pdf_to_images(new_file)
            # PDF ファイルのバイナリデータを取得

            if "button" not in st.session_state:
                old_file=None
                new_file=None
                st.session_state['flag'] = 'true'

            st.title("少々お待ちください。")
            pdf_data = diffPDF(old_file,new_file)
            st.header('完了')
            st.session_state['button'] = st.download_button(label="Download PDF", data=pdf_data, file_name="output.pdf", mime="application/pdf")
            # PDF ファイルをダウンロード可能なリンクとして表示
            
            
def restart():
    st.title("再度使用するにはページの再読み込みをお願いします")
            # ダウンロードボタンのラベルとファイル名
            # download_button_label = "Download File"
            # file_name = os.path.basename(pdf_data)
            # st.markdown(get_binary_file_downloader_html(file_path, download_button_label, file_name), unsafe_allow_html=True)
 
def convert_pdf_to_images(uploaded_file):
    pdf_bytes = uploaded_file.read()
    images = convert_from_bytes(pdf_bytes)
    return images



# 中間データ用のフォルダを作成。2回目以降は中のファイルを削除
# def empty_folder(folder_path):
#     # フォルダ内のファイルを削除
#     for filename in os.listdir(folder_path):
#         file_path = os.path.join(folder_path, filename)
#         try:
#             if os.path.isfile(file_path) or os.path.islink(file_path):
#                 os.unlink(file_path)
#             elif os.path.isdir(file_path):
#                 # サブフォルダ内のファイルも削除
#                 empty_folder(file_path)
#                 # サブフォルダを削除
#                 os.rmdir(file_path)
#         except Exception as e:
#             print(f"削除エラー: {e}")



def diffPDF(oldfilename,newfilename):
    # temp_path = os.environ.get('TEMP')+"\PDFdiff"
    # temp_path = "\PDFdiff"
    # if not os.path.isdir(temp_path):
    #     os.makedirs(temp_path)
    
    # empty_folder(temp_path)
    
    
    #この1文で変換されたjpegファイルが、imageホルダー内に作られます。
    # pngに変更。jpegは画質が悪い
    # with tempfile.TemporaryDirectory() as td:
        # TEMPファイルを作ってその都度削除しようとしたが、フォルダの削除がセキュリティに引っかかるっぽくてやめた
    print("旧ファイル変換中")
    pdf_bytes = oldfilename.read()
    # page = convert_from_path(oldfilename, output_folder=temp_path,fmt='png',dpi=500,output_file="old")
    page = convert_from_bytes(pdf_bytes,fmt='png',dpi=500)
    del oldfilename
    
    leng = int(len(page))
    oldpng=[]
    # 一度pngにしたものをnumpyに変換
    for i in range(leng):
        oldpng.append(np.array(page[i]))
    # file_list = glob.glob(os.path.join(temp_path, "*.png"))
    # oldpng=[]
    # for file_path in file_list:
    #     oldpng.append(np.array(Image.open(file_path)))
    # with tempfile.TemporaryDirectory() as td:
        
    print("新ファイル変換中")
    pdf_bytes = newfilename.read()
    # page = convert_from_path(oldfilename, output_folder=temp_path,fmt='png',dpi=500,output_file="old")
    page = convert_from_bytes(pdf_bytes,fmt='png',dpi=500)
    
    # page = convert_from_path(newfilename, output_folder=temp_path,fmt='png',dpi=500,output_file="new")
    leng = int(len(page))
    newpng=[]
    for i in range(leng):
        newpng.append(np.array(page[i]))
    # file_list = glob.glob(os.path.join(temp_path, "*.png"))
    # newpng=[]
    # for file_path in file_list:
    #     newpng.append(np.array(Image.open(file_path)))
    
    # im_marge=[]
    leng = int(len(oldpng))
    # with tempfile.TemporaryDirectory() as td:
    print("比較合成中")
    lists=[]

    for i in range(leng):
        # im_r = newpng[i]
        pixel_sum = np.sum(newpng[i], axis=2)
        newpng[i][:, :, 1] = np.where(pixel_sum > 730, 255, 0) #簡易的に2値化(Rayco等のカラーPDF対策)
        #赤要素のみ残す
        newpng[i][:,:,0]=255
        newpng[i][:,:,2]=255
        
        # im_b = oldpng[i]
        pixel_sum = np.sum(oldpng[i], axis=2)
        oldpng[i][:, :, 0] = np.where(pixel_sum > 730, 255, 0)
        # 青要素のみ残す
        oldpng[i][:,:,2]=255
        oldpng[i][:,:,1]=255
        # NumPy配列をPIL Imageに変換
        temp_array = np.minimum(newpng[i],oldpng[i]) # 合成
        output_array=temp_array.astype(np.uint8)
        pil_image = Image.fromarray(output_array)
        
        # 画像をPNG形式で保存
        # output_filename = str(temp_path)+"\\"+str(i)+"out.png"
        buffered = BytesIO()
        pil_image.save(buffered, format="png")

        lists.append(buffered)
        # im_marge.append(im_r + im_b)
        
    # output_image = Image.fromarray(im_marge)
    # plt.imshow(pil_image)
    
    # PDFファイル出力
    # pdfpath = temp_path+"\output_diff.pdf"
    # lists = list(glob.glob(os.path.join(temp_path, "*out.png")))
    # with open(pdfpath,"wb") as f:
    #     f.write(img2pdf.convert([str(i) for i in lists if ".png" in i]))
    # root.destroy()
    images = img2pdf.convert([i.getvalue() for i in lists])
    # images = img2pdf.convert([i for i in lists])# if ".png" in i])
    return images
    
if __name__ == "__main__":
    if "flag" not in st.session_state:
        main()
    else:
        restart()