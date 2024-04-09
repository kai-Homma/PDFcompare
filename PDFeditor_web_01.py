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
        st.text('比較したいファイルをアップしてもらうと比較図を作成し、ページ下にDLボタンが現れます  \n ※基板図を想定しているので、何十枚ものPDFになるとメモリが足りなくてエラーになる可能性があります…')
        st.subheader('旧ファイル')
        old_file = st.file_uploader("変更前のPDFファイルを入れて下さい", type="pdf", key="1234")
        st.subheader('新ファイル')
        new_file = st.file_uploader("変更後のPDFファイルを入れて下さい", type="pdf", key="0000")

        
        if old_file is not None:
            if new_file is not None:       
                    st.session_state['flag'] = True
                    st.subheader("少々お待ちください。")
                    pdf_data = diffPDF(old_file,new_file)
                    
                    if st.session_state['flag'] == True:
                        st.subheader('完了')
                        st.balloons()
                        # PDF ファイルをダウンロード可能なリンクとして表示
                        st.session_state['button'] = st.download_button(label="Download PDF", data=pdf_data, file_name="output.pdf", mime="application/pdf")
    
    if st.session_state['flag'] == "page":
        st.title("PDFのページ数は合わせてください")
        st.button("OK")
        st.title("再度使用するにはページの再読み込みをお願いします")
    
    if st.session_state['flag'] == True:
        st.title("再度使用するにはページの再読み込みをお願いします")
        
# @profile                
def diffPDF(oldfilename,newfilename):
    print("旧ファイル変換中")
    # PDF ファイルのバイナリデータを取得
    pdf_bytes = oldfilename.read()
    # 一度png形式へ変換
    page = convert_from_bytes(pdf_bytes,fmt='png',dpi=450)
    leng = int(len(page))
    del oldfilename #
    
    print("新ファイル変換中")
    pdf_bytes = newfilename.read()
    # 一度png形式へ変換
    newpage = convert_from_bytes(pdf_bytes,fmt='png',dpi=450)
    newleng = int(len(newpage))
    del newfilename #メモリ開放
    
    if leng is not newleng:
        st.session_state['flag'] = "page"
        return 0
    
    lists=[]   
    # 一度pngにしたものをnumpyに変換
    for i in range(leng):
        oldpng=np.array(page[i])
        pixel_sum = np.sum(oldpng, axis=2)
        oldpng[:, :, 0] = np.where(pixel_sum > 730, 255, 0)
        # 青要素のみ残す
        oldpng[:,:,2]=255
        oldpng[:,:,1]=255
        
        newpng=np.array(page[i])
        pixel_sum = np.sum(newpng, axis=2)
        newpng[:, :, 1] = np.where(pixel_sum > 730, 255, 0) #簡易的に2値化(Rayco等のカラーPDF対策)
        #赤要素のみ残す
        newpng[:,:,0]=255
        newpng[:,:,2]=255
        # 合成
        oldpng = np.minimum(newpng,oldpng)
        pil_image = Image.fromarray(oldpng.astype(np.uint8))
        # バッファにpngとして保存
        buffered = BytesIO()
        pil_image.save(buffered, format="png")
        lists.append(buffered)

    del page #メモリ開放
    del pixel_sum
    del newpng
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