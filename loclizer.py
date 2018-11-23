from google.cloud import translate
from google.cloud import vision_v1p3beta1 as vision
from PIL import Image
from PIL import ImageDraw
import sys
import datetime

def translate_ja(text):
	# Client API 初期化
    translate_client = translate.Client()
    # 翻訳
    translation = translate_client.translate(
        text,
        target_language='ja')

    result = translation['translatedText']
    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(result))

    return result

def view_results(path, objects):
	# 画像表示
    im = Image.open(path)
    (im_w, im_h) = im.size
    draw = ImageDraw.Draw(im)

    for object_ in objects:
    	# 返された結果を日本語に変換
        name_ja = translate_ja(object_.name)
        print('\n{} (confidence: {})'.format(name_ja, object_.score))

        poly_xy =[] 

        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
            poly_xy.append((vertex.x * im_w, vertex.y * im_h))

        # 対象物の周辺に多角形を描画
        draw.polygon(poly_xy, outline=(255, 0, 0))
        text_x = poly_xy[0][0] + (im_w * 0.05)
        text_y = poly_xy[0][1] - (im_h * 0.03) 
        # ラベル付与
        draw.text((text_x, text_y), object_.name , fill=(255, 0, 0))
    # 画像保存
    im.save("/home/takuma/prog/18advent/save/result.jpg")


def localize_objects(path):
	# Client API 初期化
    client = vision.ImageAnnotatorClient()
    # 画像読み込み
    with open(path, 'rb') as image_file:
        content = image_file.read().
    # Object Loclizer へリクエストを送信し、結果を取得
    image = vision.types.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations
    print('Number of objects found: {}'.format(len(objects)))

    return objects

if __name__ == '__main__':
    if len(sys.argv) < 3:
    	exit(1)
    path = sys.argv[1]
    save_dir = sys.argv[2]
    # GCP Object Loclizerを呼び出して結果を取得
    detected_objects = localize_objects(path)
    # 結果表示
    view_results(path, detected_objects)
