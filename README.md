# Đồ Án Chuyên Ngành 1
===================================================
## Đề tài: Nhận dạng biển số xe (Number Plate Recognition)
### Thực hiện: __Lưu Quang Vũ, Trần Văn Quốc Đạt__

#### Quá trình thực hiện
- Cài đặt các thư viện cho xử lý ảnh
- Viết chương trình cho *Server* bao gồm:
  - Tạo *Server* để lắng nghe các yêu cầu kết nối từ *Client*
  - Nhận dữ liệu thừ *Client* và giải mã dữ liệu
  - Xử lý hình ảnh và yêu cầu *Client* mở/đóng cổng
  - Lưu, truy xuất, tìm kiếm dữ liệu từ *Database*
    
- Viết chương trình cho *Client* bao gồm:
  - Gửi yêu cầu kết nối đến *Server*
  - Nhận tín hiệu ra/vào cổng để gửi yêu cầu xử lý hình ảnh lên *Server*
  - Giải mã tín hiệu từ *Server* gửi về và xử lý
  - Đếm vị trí còn trống trong bãi, nếu đầy thì chỉ mở cổng ra không mở cổng vào
- Tạo nơi lưu trữ dữ liệu và kết nối với *Server*
- Tạo giao diện cho dự án gồm giao diện chính và giao diện tìm kiếm

#### Ưu nhược điểm:
--------------------
Ưu điểm:
- Nhận diện biển số xe
- Lưu vào cơ sở dữ liệu gồm biển số dạng text, hình ảnh (in/out), thời gian (in/out), thời gian (in/out)
- Đếm vị trí còn trống trong bãi đỗ
- Mã hóa dữ liệu (AES) giữa client và server
- Giao diện dễ sử dụng

Nhược diểm:
- Chỉ nhận diện được biển *số ngang*, còn *biển vuông* thì chưa
- Nhận dạng chưa chính xác các ký tự đặt biệt như *A* thành *H*,...
- Nhận diện còn phụ thuộc vào môi trường như ánh sáng,...
