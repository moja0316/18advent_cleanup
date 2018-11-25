from tinydb import TinyDB, Query


def get_diagonal_vertex(vertices):
    xpoints = [a["x"] for a in vertices]
    ypoints = [a["y"] for a in vertices]
    return ({"x": min(xpoints), "y": min(ypoints)}, {"x": max(xpoints), "y": max(ypoints)})

# 不達の
def check_analogy(objects_json1, objects_json2):
    # 左上と右下を検出
    ul_1, br_1 = get_diagonal_vertex(objects_json1["vertices"])
    ul_2, br_2 = get_diagonal_vertex(objects_json2["vertices"])
    print("ul_1 {}".format(ul_1))
    print("br_1 {}".format(br_1))
    print("ul_2 {}".format(ul_2))
    print("br_2 {}".format(br_2))

    # 重なりの頂点を検索
    synth_ul = {"x": max(ul_1["x"], ul_2["x"]), "y": max(ul_1["y"], ul_2["y"])}
    synth_br = {"x": min(br_1["x"], br_2["x"]), "y": min(br_1["y"], br_2["y"])}

    synth_w = synth_br["x"] - synth_ul["x"]
    synth_h = synth_br["y"] - synth_ul["y"]

    # 重なりがあるか確認
    if synth_w <= 0 and synth_h <=0:
        return 0

    #重なりの割合をJaccard類似度で表現し返却
    obj1_w = br_1["x"] - ul_1 ["x"]
    obj1_h = br_1["y"] - ul_1 ["y"]
    obj2_w = br_2["x"] - ul_2 ["x"]
    obj2_h = br_2["y"] - ul_2 ["y"]
    area_synth = synth_h * synth_w
    area_only_obj1 = obj1_h * obj1_w - area_synth
    area_only_obj2 = obj2_h * obj2_w - area_synth
    analogy = area_synth / (area_synth + area_only_obj1 + area_only_obj2)
    print("analogy : {}".format(analogy))
    return analogy
    
# GCPの戻り値の必要な部分だけjsonに変換
def convert_to_objects_json(detected_objects):
    ret = []
    for obj in detected_objects:
        buf = {}
        buf["name"] = obj.name
        vert = [{"x" : v.x, "y" :v.y} for v in obj.bounding_poly.normalized_vertices]
        buf["vertices"] = vert
        ret.append(buf)
    return ret

def save_data(detected_objects_json):
    db = TinyDB("detected.json")
    db.insert_multiple(detected_objects_json)


def get_saved_data(serach_key):
    db = TinyDB("detected.json")
    query = Query()
    searched = db.search(query.name == serach_key)
    return searched


def remove_all():
    db = TinyDB("detected.json")
    db.purge()

# 前回に識別されたデータと似た位置に同じオブジェクトがあるかチェック
def check_analogy_object_from_past(detected_objects):
    detected_json = convert_to_objects_json(detected_objects)
    analogy_objects = []
    for d in detected_json:
        # 前回のデータから同じ名前のオブジェクトを取得
        past_json = get_saved_data(d["name"])
        for p in past_json:
            analogy = check_analogy(d,p)
            if analogy > 0.8:
                analogy_objects.append(d)
    # DB内のデータを書き換え
    remove_all()
    save_data(detected_json)
    return analogy_objects