import localizer
import analogy_detector
import picamera
import sys
import subprocess
import datetime
import time
from PIL import Image as im

# Raspberry Piで撮影
def take_photo():
    # セットアップ、解像度を(1280, 720)に
    camera = picamera.PiCamera()
    camera.resolution = (1280, 720)
    # ファイル名セット
    now = datetime.datetime.now()
    pname = "/home/pi/img/"+ now.strftime("%y%m%d%H%M%S") + ".jpg"
    triname = "/home/pi/img/"+ now.strftime("%y%m%d%H%M%S") + "_tri.jpg"
    # 撮影
    camera.capture(pname)
    print("Photo taken filename : {}".format(pname))
    # トリミング
    org_img = im.open(pname)
    w, h = org_img.size
    tri_img = org_img.crop((w * 0.3, h * 0.2, w * 0.8, h * 0.6))
    tri_img.save(triname)
    print("Trimmed filename : {}".format(triname))
    return triname

def execute(imgpath, save_dir):
    # GCP Object Loclizerを呼び出して結果を取得
    detected_objects = localizer.localize_objects(imgpath)
    # 結果表示
    localizer.view_results(imgpath, save_dir, detected_objects)
    analogied_objects = analogy_detector.check_analogy_object_from_past(detected_objects)
    
    for ao in analogied_objects:
        # 名前を日本語に変換
        name_ja = localizer.translate_ja(ao["name"])
        msg = "{:.2f}".format(ao["vertices"][0]["x"]) + "、" + "{:.2f}".format(ao["vertices"][0]["y"]) + "付近の" + name_ja + "が放置されています。片づけましょう。"
        cmds = ['node', 'google-home-notifier/notify.js', msg]
        print(msg)
        # google-home-notifierを起動
        subprocess.call(cmds)
        # 連続して発言する場合に備えて余白を確保
        time.sleep(6)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Err : save_dir is not set.")
        sys.exit(1)
    save_dir = sys.argv[1]
    execute(take_photo(), save_dir)