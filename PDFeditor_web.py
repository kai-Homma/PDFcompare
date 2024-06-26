# -*- coding: utf-8 -*-
# """
# Created on Thu Jan  4 13:52:26 2024

# cd C:\Users\HOMMA.KAI.P\Desktop\python\PDFdiff
# streamlit run PDFeditor_web.py

# @author: HOMMA.KAI
# """

import streamlit as st

# import os
from pdf2image import convert_from_bytes
from PIL import Image
import numpy as np
import img2pdf
from io import BytesIO

# from memory_profiler import profile

def main():

    st.set_page_config(
        page_title="PDF-App",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    if st.session_state['flag'] == False:
        st.title("PDF比較")
        st.text('比較したいファイルをアップしてもらうと比較図を作成し、ページ下にDLボタンが現れます  \n ※A3サイズで12枚以上ぐらいになるとメモリが足りなくてエラーになる可能性があります…')
        st.subheader('旧ファイル')
        old_file = st.file_uploader("変更前のPDFファイルを入れて下さい", type="pdf", key="1234")
        st.subheader('新ファイル')
        new_file = st.file_uploader("変更後のPDFファイルを入れて下さい", type="pdf", key="0000")
        
    
        
        if old_file is not None:
            if new_file is not None:       

                    st.subheader("少々お待ちください。")
                    pdf_data = diffPDF(old_file,new_file)
                    st.session_state['flag'] = True
                     
                    st.subheader('完了')
                    st.balloons()
                    # PDF ファイルをダウンロード可能なリンクとして表示
                    st.session_state['button'] = st.download_button(label="Download PDF", data=pdf_data, file_name="output.pdf", mime="application/pdf")
            
    
    if st.session_state['flag'] == True:
        st.title("再度使用するにはページの再読み込みをお願いします")
        
# @profile                
def diffPDF(oldfilename,newfilename):
    print("旧ファイル変換中")
    # PDF ファイルのバイナリデータを取得
    pdf_bytes = oldfilename.read()
    # 一度png形式へ変換
    page = convert_from_bytes(pdf_bytes,fmt='png',dpi=450)
    del oldfilename #メモリ開放
    
    leng = int(len(page))
    oldpng=[]
    # 一度pngにしたものをnumpyに変換
    for i in range(leng):
        oldpng.append(np.array(page[i]))
        pixel_sum = np.sum(oldpng[i], axis=2)
        oldpng[i][:, :, 0] = np.where(pixel_sum > 730, 255, 0)
        # 青要素のみ残す
        oldpng[i][:,:,2]=255
        oldpng[i][:,:,1]=255
        
    print("新ファイル変換中")
    # PDF ファイルのバイナリデータを取得
    pdf_bytes = newfilename.read()
    # 一度png形式へ変換
    page = convert_from_bytes(pdf_bytes,fmt='png',dpi=450)
    del newfilename #メモリ開放
    leng = int(len(page))
    # 一度pngにしたものをnumpyに変換
    for i in range(leng):
        newpng=np.array(page[i])
        pixel_sum = np.sum(newpng, axis=2)
        newpng[:, :, 1] = np.where(pixel_sum > 730, 255, 0) #簡易的に2値化(Rayco等のカラーPDF対策)
        #赤要素のみ残す
        newpng[:,:,0]=255
        newpng[:,:,2]=255
        # 合成
        oldpng[i] = np.minimum(newpng,oldpng[i])

    del page #メモリ開放
    del pixel_sum
    del newpng
    
    leng = int(len(oldpng))
    print("比較合成中")
    lists=[]       

    for i in range(leng): 
        pil_image = Image.fromarray(oldpng[i].astype(np.uint8))
        
        # バッファにpngとして保存
        buffered = BytesIO()
        pil_image.save(buffered, format="png")
        lists.append(buffered)
    del buffered,oldpng
    
    # PDFファイル出力
    images = img2pdf.convert([i.getvalue() for i in lists])
    del lists
    # images = img2pdf.convert([i for i in lists])# if ".png" in i])
    return images
    
if __name__ == "__main__":
    if "button" not in st.session_state:
        st.session_state['button'] = False
    if "flag" not in st.session_state:
        st.session_state['flag'] = False
          
        
    main()