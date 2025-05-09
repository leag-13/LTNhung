import cv2
import numpy as np, time
CLASSES = ['unknown', 'left', 'right', 'straight', 'stop', 'walk', 'turn_around']
traffic_sign_model = cv2.dnn.readNetFromONNX("traffic_sign_classifier.onnx")

# Process phát hiện biển báo
def process_traffic_sign_loop(g_image_queue):
    while True:
        if g_image_queue.empty():
            time.sleep(0.1)
            continue
        image = g_image_queue.get()

        # Chuẩn bị 1 hình ảnh để vẽ kết quả
        draw = image.copy()
        # Phát hiện biển báo
        detect_traffic_signs(image, traffic_sign_model, draw=draw)
        # Hiện kết quả
        cv2.imshow("Traffic signs", draw)
        cv2.waitKey(1)

def enhance_gamma(image, gamma=0.6):
    """Áp dụng gamma correction để làm sáng vùng tối"""
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(256)]).astype("uint8")
    return cv2.LUT(image, table)

def filter_signs_by_color(image):
    """Lọc biển báo màu đỏ tối và xanh dương trong điều kiện ngược sáng"""

    # 1. Tăng sáng vùng tối bằng gamma correction
    img_gamma = enhance_gamma(image, gamma=0.6)

    # 2. Lọc màu đỏ trong không gian LAB (kênh a)
    lab = cv2.cvtColor(img_gamma, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    lower_a = 150
    upper_a = 255
    mask_red = cv2.inRange(a, lower_a, upper_a)

    # 3. Lọc màu xanh dương trong không gian HSV
    hsv = cv2.cvtColor(img_gamma, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 30, 50])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # 4. Kết hợp mask đỏ và xanh dương
    mask_combined = cv2.bitwise_or(mask_red, mask_blue)

    # 5. Làm sạch mask với phép toán hình thái
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_clean = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, kernel)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel)

    return mask_clean

def get_boxes_from_mask(mask):
    """Tìm kiếm hộp bao biển báo
    """
    bboxes = []

    nccomps = cv2.connectedComponentsWithStats(mask, 4, cv2.CV_32S)
    numLabels, labels, stats, centroids = nccomps
    im_height, im_width = mask.shape[:2]
    for i in range(numLabels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        # Lọc các vật quá nhỏ, có thể là nhiễu
        if w < 20 or h < 20:
            continue
        # Lọc các vật quá lớn
        if w > 0.8 * im_width or h > 0.8 * im_height:
            continue
        # Loại bỏ các vật có tỷ lệ dài / rộng quá khác biệt
        if w / h > 2.0 or h / w > 2.0:
            continue
        bboxes.append([x, y, w, h])
    return bboxes


def detect_traffic_signs(img, model, draw=None):
    mask   = filter_signs_by_color(img)
    bboxes = get_boxes_from_mask(mask)
    signs  = []

    for (x, y, w, h) in bboxes:
        sub = img[y:y+h, x:x+w]
        if sub.shape[0] < 20 or sub.shape[1] < 20: continue

        blob = cv2.dnn.blobFromImage(sub, scalefactor=1/255.0,
                                     size=(128,128), swapRB=True)
        model.setInput(blob)
        preds = model.forward()[0]
        cls   = int(np.argmax(preds))
        score = float(preds[cls])

        if cls == 0 or score < 0.95: continue
        signs.append([CLASSES[cls], x, y, w, h, score])

        if draw is not None:
            cv2.rectangle(draw, (x,y), (x+w,y+h), (0,255,255), 3)
            cv2.putText(draw, f"{CLASSES[cls]} {score:.2f}", (x, y-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    return signs

# ------------------------------------------------------------
def detect_single_sign(frame, model, conf_thres=0.5):
    signs = detect_traffic_signs(frame, model, draw=None)
    if not signs:
        return 'unknown', 0.0
    best = max(signs, key=lambda s: s[-1])         # [-1] giờ là score
    label, score = best[0], best[-1]
    return (label, score) if score >= conf_thres else ('unknown', score)