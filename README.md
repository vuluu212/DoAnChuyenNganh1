# Đồ Án Chuyên Ngành 1
## Đề tài: Nhận dạng biển số xe (Number Plate Recognition)
### Thực hiện bởi: 
- *Lưu Quang Vũ*
- *Trần Văn Quốc Đạt*

[Link bài báo cáo Đồ án chuyên ngành 1](https://docs.google.com/document/d/1AHISBgSxSUhjXrb8DtjoLRXv2xVi0Q4H/edit?usp=sharing&ouid=106940902399053081489&rtpof=true&sd=true)
### Các bước thực hiện
--------------------
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

### Kết quả thực hiện: 
--------------------


- Giao diện chương trình chính

![image](https://github.com/user-attachments/assets/1cb9e70c-9294-4624-adc5-f1c2c8898cdf)

- Phát hiện biển số, phân tích và hiển thị lên giao diện

![image](https://github.com/user-attachments/assets/867587db-56d2-459d-ac96-cdbf678af4af)

- Giao diện truy vấn dữ liệu

![image](https://github.com/user-attachments/assets/872c7e8e-dcf0-4b71-9208-9cd5d5eeb4c7)

- *Server* lắng nghe kết nối và chấp nhận kết nối

![image](https://github.com/user-attachments/assets/3d490f6e-941d-42fd-bb1f-7c8d2168fb5d)

- *Client* gửi yêu cầu đọc biển số lên *Server*

![image](https://github.com/user-attachments/assets/72c58830-d715-4ade-8a61-e2e0c5886b55)

- Phát hiện, xử lý biển số xe và yêu cầu mở cổng

![image](https://github.com/user-attachments/assets/f48aff0f-f5fe-4263-b860-1f86af2d8713)

- Xử lý yêu cầu cổng ra bãi đỗ

![image](https://github.com/user-attachments/assets/8923bbef-45ee-474a-9146-05c73e6ad149)

### Ưu nhược điểm:
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

### Tài liệu tham khảo
---------------
[1]:  Simarpreet Singh (2020), Detecting Geometrical Shapes in an image using OpenCV, 10/05/2024, từ <https://dev.to/simarpreetsingh019/detecting-geometrical-shapes-in-an-image-using-opencv-4g72?comments_sort=latest>

[2]:  Nguyễn Chiến Thắng (2019), [Nhận diện biển số xe] Chương 4 – Nhận diện biển số xe bằng WPOD và Tesseract OCR, 29/4/2024, từ < https://www.miai.vn/2019/11/30/nhan-dien-bien-so-xe-chuong-4-nhan-dien-bien-so-xe-bang-wpod-va-tesseract-ocr/>

[3]: Emma Yu (2023), Tiêu chuẩn mã hóa dữ liệu AES là gì và các chế độ hoạt động của AES, 4/5/2024, từ < https://hoanghamobile.com/tin-tuc/aes/>

[4]: markhermy3100 (2024), Tất Tần Tật Về Block Cipher, 4/5/2024, từ < https://codelearn.io/sharing/tat-tan-tat-ve-block-cipher>

[5]:  Huỳnh Công Pháp, Bài giảng lập trình mạng. Khoa khoa học máy tính trường đại học Công nghệ thông tin và Truyền thông Việt – Hàn

[6]: Chris Dahms (2016), OpenCV 3 License Plate Recognition Python. <https://www.youtube.com/watch?v=fJcl6Gw1D8k>
