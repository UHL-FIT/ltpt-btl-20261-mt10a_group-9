import cv2 as cv

cam = cv.VideoCapture(0, cv.CAP_DSHOW)

try:
    if not cam.isOpened():
        print('Lỗi: Không thể mở camera !')
    else:
        print('Camera đã sẵn sàng !')
        while True:
            res, frame = cam.read()
            if not res:
                print('Lỗi: Đọc khung hình không thành công !')
                break
            
            # Lật ảnh cho giống soi gương
            flipped_frame = cv.flip(frame, 1)
            cv.imshow('TEST CAMERA', flipped_frame)

            # Nhấn q để thoát
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

except Exception as e:
    print(f'Lỗi phát sinh: {e}')

finally:
    # Chỉ cần một chỗ dọn dẹp duy nhất ở đây là đủ
    cam.release()
    cv.destroyAllWindows()
    print('Hệ thống đã dọn dẹp và đóng an toàn !')