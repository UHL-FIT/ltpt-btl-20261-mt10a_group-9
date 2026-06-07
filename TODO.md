# TODO - SmartAttend (Xóa sinh viên)

- [x] Bổ sung UI nút **Xóa sinh viên** trong trang **Đăng ký** (views/ctk_view.py).

- [x] Tạo popup nhập MSV khi bấm nút, có nút **Xác nhận/Hủy**, và validate (controllers/ctk_controller.py).


- [ ] Callback “Xác nhận” gọi `models.face_attendance.delete_student(msv)`; nếu OK hiện messagebox “Xóa thành công”.
- [ ] Sau khi người dùng bấm OK ở messagebox thành công: đóng toàn bộ popup để quay về giao diện trước khi bấm nút.
- [ ] Test thủ công: thêm SV -> bấm Xóa -> nhập đúng MSV -> xác nhận xóa.

