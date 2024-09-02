import cv2 
from pytesseract import pytesseract
from PIL import Image
import mysql.connector
import datetime
from lib_detection import load_model, detect_lp, im2single
import socket
import time
import threading
import shutil
import os
import sys
import uuid
from Crypto.Cipher import AES
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from NumberPlateUI import Ui_MainWindow
from SearchNumberPlateGUI import Ui_FMainWindow_search
from PyQt5.QtCore import *
from PyQt5.QtGui import *

db = mysql.connector.connect(user="root",password="",host="localhost",database="quanlyxe")

key = b'doanchuyennganhm'
cipher = AES.new(key, AES.MODE_ECB)
# HOST = '192.168.1.98'  # Thay đổi thành địa chỉ IP của máy tính chạy server
HOST = '172.20.10.2'  # Thay đổi thành địa chỉ IP của máy tính chạy server
PORT = 8090
status_camera = 0
mocong = 0
source_file = r"G:\Number_Plate_Recognition\image_check\numberplate.jpg"  # Đường dẫn đến tệp ảnh biển số
source_files = r"G:\Number_Plate_Recognition\image_check\xe.jpg"  # Đường dẫn đến tệp ảnh nguồn xe
destination_folder = r"G:\Number_Plate_Recognition\images"  # Đường dẫn đến thư mục đích
runing_receive_data = True
is_connected = True
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Tạo socket TCP
server_socket.bind((HOST, PORT))   # Gắn socket vào địa chỉ và cổng
server_socket.listen(1)            # Lắng nghe kết nối từ client
print('Đang lắng nghe kết nối...')
client_socket, client_address = server_socket.accept()   # Chấp nhận kết nối từ client
print('Đã kết nối từ:', client_address)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)

        self.uic.btn_Start.clicked.connect(self.start_capture_video)
        self.uic.btn_stop.clicked.connect(self.exit_capture_video)
        self.uic.btn_search.clicked.connect(self.search_data)

        self.cap = None
        self.client_socket = client_socket
        self.client_address = client_address

    def start_capture_video(self):
        cam=cv2.VideoCapture(0)
        self.license_plate_recognition(client_socket, cam)
        print('s')
    
    def license_plate_recognition(self, client_socket, cam):
        global status_camera
        while True:
            ret,frame=cam.read() 
            
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)  
            # Hiển thị QImage lên lb_auto
            self.uic.lb_auto.setPixmap(QPixmap.fromImage(qImg))
            self.uic.lb_auto.setScaledContents(True)
        
            image_car = QPixmap(r'G:\Number_Plate_Recognition\image_check\xe.jpg')
            image_plate = QPixmap(r'G:\Number_Plate_Recognition\image_check\numberplate.jpg')
            self.uic.lb_auto.setPixmap(image_plate)
            self.uic.lb_auto.setScaledContents(True)
            self.uic.label.setPixmap(image_car)
            self.uic.label.setScaledContents(True)
            cv2.imwrite('image_check/xe.jpg', frame)
            # đọc từng frame
            framegray=cv2.cvtColor(frame,cv2.COLOR_BGR2BGRA)                       # thiết lập màu sắc cho ảnh
            n_plate_detector = cv2.CascadeClassifier("haarcascade_russian_plate_number.xml")     # nhúng file nhận diện biển số xe (haarcascade_russian_plate_number.xml copy trên mạng)
            detections = n_plate_detector.detectMultiScale(framegray, scaleFactor=1.05, minNeighbors=3)    # khai báo vùng biển số xe khi được file nhận dạng phát hiện
            for (x, y, w, h) in detections:                                        # tạo vòng lặp 4 tọa độ cho vùng biển số xe được phát hiện
                cv2.rectangle(framegray, (x, y), (x + w, y + h), (0, 255, 255),2)  # vẽ hình chữ nhật xung quanh vùng biển số xe 
                cv2.putText(framegray, "Bien so xe", (x - 20, y - 10),             # in chữ cạnh vùng biển số xe
                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255), 2)                   # tạo một khung chỉ chứa hình ảnh của biển số xe nhận diện được
                number_plate = framegray[y:y + h, x:x + w]                         # điểu chỉnh màu của khung trên thành tối   
                gray = cv2.cvtColor(number_plate,cv2.COLOR_BGR2GRAY)
                # cv2.imshow("Bien so xe", gray)                                     # show khung "Bien so xe" (khung chỉ chứa hình ảnh của biển số xe nhận diện được)
                cv2.imwrite('image_check/numberplate.jpg',gray)  
                self.readnumberplate(client_socket)
            if cv2.waitKey(1)==ord('q'): 
                cv2.destroyAllWindows()# Nếu ấn "Q" trên bàn phím sẽ đóng mọi khung lại
                break
              
    def readnumberplate(self, client_socket):                              # Đọc biển số xe từ ảnh đã lưu vào thư mục "images"
        global status_camera, mocong
        image_car = QPixmap(r'G:\Number_Plate_Recognition\image_check\xe.jpg')
        image_plate = QPixmap(r'G:\Number_Plate_Recognition\image_check\numberplate.jpg')
        self.uic.lb_auto.setPixmap(image_plate)
        self.uic.lb_auto.setScaledContents(True)
        self.uic.label.setPixmap(image_car)
        self.uic.label.setScaledContents(True)
        if status_camera == 1 or status_camera == 2:
            path_to_tesseract = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            pytesseract.tesseract_cmd = path_to_tesseract
            image = Image.open(r"G:\Number_Plate_Recognition\image_check\numberplate.jpg") # tạo biến text hứng string nhận được từ hình ảnh
            text = pytesseract.image_to_string(image,lang="eng")
            number_plate = ''
            for char in str(text):                          # loại bỏ khoảng trắng
                if (char.isspace() == False):
                    number_plate += char
            print("----------------------------------")
            print("Xe co bien so : " + number_plate)
            print("----------------------------------")
            
            if(number_plate != ""):
                print("----------------------------------")
                print(number_plate)
                result = self.check_text(number_plate)
                print(result)
                if result:
                    bienso = ''.join(result)
                    print("Chuỗi hợp lệ, đang kiểm tra database")
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    date_, time_ = current_time.split(' ')
                    
                    self.uic.txt_auto.setText(str(bienso))
                    self.uic.txt_date.setText(str(date_))
                    self.uic.txt_time.setText(str(time_))
                    new_file_name = '{}.jpg'.format(uuid.uuid1())  # Đường dẫn đến tệp ảnh mới trong thư mục đích
                    destination_file = os.path.join(destination_folder, new_file_name) # Sao chép và đổi tên tệp từ nguồn sang đích
                    shutil.copy(source_file, destination_file)
                    new_file_names = '{}.jpg'.format(uuid.uuid1())  # Đường dẫn đến tệp ảnh mới trong thư mục đích
                    destination_files = os.path.join(destination_folder, new_file_names) # Sao chép và đổi tên tệp từ nguồn sang đích
                    shutil.copy(source_files, destination_files)
                    check = self.checkNp(bienso)                 # Gọi hàm kiểm tra xem biển số này đã tồn tại trong daatabase chưa
                    if (check == 0 and status_camera == 1 ):  #  check == 0 and                     # Nếu "check" = 0 (Xe chưa từng đến gửi tại bãi)
                        self.insertNp(bienso, new_file_name, new_file_names)                    # Gọi hàm "insertNp" để cho xe vào gửi          
                        status_xe = 'Input'
                        
                        status_camera = 0 
                        mocong = 1 # mở cổng vào
                        with open("number_plate.txt", "a") as file:
                            file.write(f"{status_xe}, {bienso}, {current_time}, {new_file_name}, {new_file_names}\n")           # Ghi nội dung vào tệp tin và xuống dòng
                        print("Đã viết biển số vào tệp tin.") 
                        print("----------------------------------")  
                        self.send_thread(client_socket, mocong)
                    else:                                   # Nếu "check" != 0 (Xe đã từng đến gửi tại bãi)
                        check2 = self.checkNpStatus(bienso)      # Gọi hàm kiểm tra trạng thái của xe               
                        if check2 is not None:
                            if (check2[2] == 1 and status_camera == 2 ):                # Nếu trạng thái của xe bằng 1 (xe vào gửi và chưa lấy ra)                  
                                self.updateNp(check2[0], new_file_name, new_file_names)             # Gọi hàm "updateNp" lấy xe ra và cập nhật trạng thái cho xe này về 0 (đã lấy ra)        
                                status_camera = 0 
                                status_xe = 'Output'
                                mocong = 2  # mở cổng ra
                                with open("number_plate.txt", "a") as file:
                                    file.write(f"{status_xe}, {bienso}, {current_time}, {new_file_name}, {new_file_names}\n")           # Ghi nội dung vào tệp tin và xuống dòng
                                print("Đã viết biển số vào tệp tin.") 
                                print("----------------------------------")  
                                self.send_thread(client_socket, mocong)
                            else:                               # Nếu trạng thái của xe bằng 0 (xe vào gửi và lấy ra rồi) 
                                print('Bien so khong co trong co so')                # Gọi hàm "insertNp" để cho xe vào gửi
                        else:
                            print('Bien so khong co trong co so')    
                    time.sleep(5)
                else:
                    print("Chuỗi không hợp lệ") 
            else:
                print("Bien so khong xac dinh !")
        else:
            print(status_camera)
    
    def connectDB(self):
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="quanlyxe")
        return con
    
    def check_text(self, text):
        array = list(text)
        result = []
        x = 0
        for i in range(len(array)):
            if x == 0 or x == 1:
                if array[i].isdigit() and int(array[i]) >= 0 and int(array[i]) <= 9:
                    result.append(array[i])
                    x = x + 1
            if x == 2:
                if array[i].isalpha():
                    result.append(array[i].upper())
                    x = x + 1 
            if x == 3: 
                result.append('-')
                x = x + 1 
            if x > 3 and x < 9:
                if array[i].isdigit() and int(array[i]) >= 0 and int(array[i]) <= 9:
                    result.append(array[i])
                    x = x + 1               
        print(result)
        if len(result) == 9:
            return result
        else:
            return False
    
    def insertNp(self, number_plate, image_car_in, image_license_plate_in):
        con = self.connectDB()
        cursor = con.cursor()
        sql = "INSERT INTO Numberplate(number_plate,status,date_in,image_car_in, image_license_plate_in) VALUES(%s,%s,%s,%s,%s)"
        now = datetime.datetime.now()
        date_in = now.strftime("%Y/%m/%d %H:%M:%S")
        cursor.execute(sql,(number_plate,'0',date_in, image_car_in, image_license_plate_in))
        con.commit()
        cursor.close()
        con.close()
        print("VAO BAI GUI XE")
        print("Ngay gio vao : " + datetime.datetime.strftime(datetime.datetime.now(),"%Y/%m/%d %H:%M:%S"))

    def updateNp(self, Id, image_car_out , image_license_plate_out):                                   # Cập nhật bản ghi (Cho xe ra khỏi bãi)
        con = self.connectDB()
        cursor = con.cursor()
        sql = "UPDATE Numberplate SET status = 0, date_out = %s, image_car_out= %s ,image_license_plate_out= %s WHERE Id = %s"
        now = datetime.datetime.now()
        date_out = now.strftime("%Y/%m/%d %H:%M:%S")
        cursor.execute(sql,(date_out, image_car_out , image_license_plate_out, Id ))
        con.commit()
        cursor.close()
        con.close()
        print("RA KHOI BAI GUI XE")
        print("Ngay gio ra : " + datetime.datetime.strftime(datetime.datetime.now(),"%Y/%m/%d %H:%M:%S"))

    def checkNp(self, number_plate):
        con = self.connectDB()
        cursor = con.cursor()
        sql = "SELECT * FROM Numberplate WHERE number_plate = %s"
        cursor.execute(sql,(number_plate,))
        cursor.fetchall()
        result = cursor._rowcount
        # print("So ban ghi tim dc : " + str(result))
        con.close()
        cursor.close()
        return result
    # Check tên biển số và trạng thái của bản ghi gần nhất đọc từ hình ảnh lưu vào thư mục "images" 
    def checkNpStatus(self, number_plate):
        con = self.connectDB()
        cursor = con.cursor()
        sql = "SELECT * FROM Numberplate WHERE number_plate = %s ORDER BY date_in DESC LIMIT 1"
        cursor.execute(sql,(number_plate,))
        result = cursor.fetchone()
        # print("Ngay vao  : " + str(result[2]) + datetime.datetime.strftime(result[3],"%Y/%m/%d %H:%M:%S"))
        con.close()
        cursor.close()
        return result
    
    condition = 0
    def check(self, number):
        global condition
        condition = number
        return condition
    
    # Hàm xử lý luồng gửi dữ liệu
    def send_thread(selt, client_socket, moccong):
        global mocong
        if moccong == 1:   
            message = 'yeucau_mocongvao'
            print('Dữ liệu gửi đến client:', message)
            mahoa_bytes = message.encode('utf-8')
            msg = cipher.encrypt(mahoa_bytes)
            print('Dữ liệu được mã hóa:', msg.hex())
            client_socket.sendall(msg.hex().encode('utf-8'))
        if moccong == 2: 
            message = 'yeucau_mocong_ra' 
            print('Dữ liệu gửi đến client:', message)
            mahoa_bytes = message.encode('utf-8')
            msg = cipher.encrypt(mahoa_bytes)
            print('Dữ liệu được mã hóa:', msg.hex())
            client_socket.sendall(msg.hex().encode('utf-8'))

    def exit_capture_video(self):
        global is_connected
        message = QMessageBox.warning(self, "Warning", "Do you really want to exit?", QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            if self.cap is not None:
                self.cap.release()
            os.system('exit')
            sys.exit()
            
    def search_data(self):
        self.search_win = SearchWindow()
        self.search_win.show()
        
class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FMainWindow_search()
        self.ui.setupUi(self)

        self.ui.btn_Search.clicked.connect(self.search_number_plate)
        self.ui.btn_Reload.clicked.connect(self.load_data)
        self.ui.tableWidget.itemClicked.connect(self.handle_row_click)
        
        # self.ui.tableWidget.setColumnCount(3)
        # self.ui.tableWidget.setHorizontalHeaderLabels(["ID", "Number Plate", "Date"])

        self.connect_to_database()

    def connect_to_database(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="quanlyxe"
        )
        self.cursor = self.db.cursor() 
        
    def load_data(self):
        print('load data')
        sql = 'SELECT * FROM numberplate LIMIT 0, 20'
        mycrusor = db.cursor()
        mycrusor.execute(sql)
        results = mycrusor.fetchall()
        print(results)
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(0)
        self.ui.tableWidget.setRowCount(20) # tao hang
        self.ui.tableWidget.setColumnCount(8) # tao cot 
        #[hang,cot]
        self.ui.tableWidget.setItem(0, 0, QTableWidgetItem("ID"))
        self.ui.tableWidget.setItem(0, 1, QTableWidgetItem("Number Plate"))
        self.ui.tableWidget.setItem(0, 2, QTableWidgetItem("Date In"))
        self.ui.tableWidget.setItem(0, 3, QTableWidgetItem("Date Out"))
        self.ui.tableWidget.setItem(0, 4, QTableWidgetItem("Image In"))
        self.ui.tableWidget.setItem(0, 5, QTableWidgetItem("Image Plate In"))
        self.ui.tableWidget.setItem(0, 6, QTableWidgetItem("Image Out"))
        self.ui.tableWidget.setItem(0, 7, QTableWidgetItem("Image Plate Out"))
        table_row = 1
        print(results)
        
        for row in results:
            self.ui.tableWidget.setItem(table_row, 0, QTableWidgetItem(str(row[0])))
            self.ui.tableWidget.setItem(table_row, 1, QTableWidgetItem(row[1]))
            self.ui.tableWidget.setItem(table_row, 2, QTableWidgetItem(str(row[3])))
            self.ui.tableWidget.setItem(table_row, 3, QTableWidgetItem(str(row[4])))
            self.ui.tableWidget.setItem(table_row, 4, QTableWidgetItem(str(row[5])))
            self.ui.tableWidget.setItem(table_row, 5, QTableWidgetItem(str(row[6])))
            self.ui.tableWidget.setItem(table_row, 6, QTableWidgetItem(str(row[7])))
            self.ui.tableWidget.setItem(table_row, 7, QTableWidgetItem(str(row[8])))
            table_row += 1
            
    def search_number_plate(self):
        print('search_number_plate')
        number_plate = self.ui.txt_search.toPlainText().strip()
        if number_plate:
            sql = "SELECT * FROM numberplate WHERE number_plate LIKE %s"
            mycursor = db.cursor()
            mycursor.execute(sql, (f'{number_plate}%',))
            results = mycursor.fetchall()
            # Clear the table before displaying the search results
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.setColumnCount(0) # tao cot 
            self.ui.tableWidget.setRowCount(20) # tao hang
            self.ui.tableWidget.setColumnCount(8) # tao cot 
            #[hang,cot]
            self.ui.tableWidget.setItem(0, 0, QTableWidgetItem("ID"))
            self.ui.tableWidget.setItem(0, 1, QTableWidgetItem("Number Plate"))
            self.ui.tableWidget.setItem(0, 2, QTableWidgetItem("Date In"))
            self.ui.tableWidget.setItem(0, 3, QTableWidgetItem("Date Out"))
            self.ui.tableWidget.setItem(0, 4, QTableWidgetItem("Image In"))
            self.ui.tableWidget.setItem(0, 5, QTableWidgetItem("Image Plate In"))
            self.ui.tableWidget.setItem(0, 6, QTableWidgetItem("Image Out"))
            self.ui.tableWidget.setItem(0, 7, QTableWidgetItem("Image Plate Out"))
            table_row = 1
            for row in results:
                self.ui.tableWidget.setItem(table_row, 0, QTableWidgetItem(str(row[0])))
                self.ui.tableWidget.setItem(table_row, 1, QTableWidgetItem(row[1]))
                self.ui.tableWidget.setItem(table_row, 2, QTableWidgetItem(str(row[3])))
                self.ui.tableWidget.setItem(table_row, 3, QTableWidgetItem(str(row[4])))
                self.ui.tableWidget.setItem(table_row, 4, QTableWidgetItem(str(row[5])))
                self.ui.tableWidget.setItem(table_row, 5, QTableWidgetItem(str(row[6])))
                self.ui.tableWidget.setItem(table_row, 6, QTableWidgetItem(str(row[7])))
                self.ui.tableWidget.setItem(table_row, 7, QTableWidgetItem(str(row[8])))
                table_row += 1 
            mycursor.close()

    def handle_row_click(self, item):
        # Lấy hàng được chọn
        print('handle_row_click')
        # Lấy dữ liệu của hàng được chọn
        row = item.row()
        print(row)
        id = self.ui.tableWidget.item(row, 0).text()
        number_plate = self.ui.tableWidget.item(row, 1).text()
        date_in = self.ui.tableWidget.item(row, 2).text()
        date_out = self.ui.tableWidget.item(row, 3).text()
        image_data_in_plate = self.ui.tableWidget.item(row, 4).text()
        image_data_in = self.ui.tableWidget.item(row, 5).text()
         # Hiển thị ảnh lên QLabel
        image_path = f"images\\{image_data_in}"
        image_path_plate = f"images\\{image_data_in_plate}"
        image = QPixmap(image_path)
        images = QPixmap(image_path_plate)
        self.ui.txt_number.setText(f"{number_plate}")
        self.ui.txt_datein.setText(f"{date_in}")
        self.ui.txt_dateout.setText(f"{date_out}")
       
        self.ui.image_plate.setPixmap(images)
        self.ui.image_plate.setScaledContents(True)
        self.ui.image_car.setPixmap(image)
        self.ui.image_car.setScaledContents(True)        
        
# Hàm xử lý luồng nhận dữ liệu
def receive_thread(client_socket):
    global is_connected  # Sử dụng biến toàn cục 'is_connected'
    global status_camera
    while is_connected:
        try:
            # Nhận dữ liệu từ client
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print('Client đã ngắt kết nối')
                break
            print('Dữ liệu nhận được từ client:', data)
            encrypted_msg = bytes.fromhex(data)  # Convert the encrypted message from hex to bytes
            decrypted_msg = cipher.decrypt(encrypted_msg).decode('utf-8')  # Decrypt the message and decode it to a string
            print('Dữ liệu sau khi giải mã:',decrypted_msg)    
            if (decrypted_msg == 'docbienso_dauvao') : # be176893a0d371509acbc5e10e66346c
                print('1')                
                status_camera = 1
            elif decrypted_msg == 'docbienso_dau_ra': #92f9331644ce13fa8d5e3da0e449eb24
                print('2')                
                status_camera = 2
            else:
                message = 'yeucaukhonghople' #2809fa117ce0d67b1f90ca4fb16536d0
                print('Dữ liệu gửi đến client:', message)
                mahoa_bytes = message.encode('utf-8')        
                msg = cipher.encrypt(mahoa_bytes)  # Convert the message to bytes
                print('Dữ liệu được mã hóa:', msg.hex())
                client_socket.sendall(msg.hex().encode('utf-8'))
        except ConnectionResetError:
            print('Kết nối đã bị đóng từ phía client')
            break
    is_connected = False  # Đặt lại trạng thái kết nối
    
# Hàm xử lý luồng nhận dữ liệu
def receive_thread(client_socket):
    global is_connected 
    global status_camera
    while is_connected:
        try: 
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print('Client đã ngắt kết nối')
                break
            print('Dữ liệu nhận được từ client:', data)
            encrypted_msg = bytes.fromhex(data)  # Convert the encrypted message from hex to bytes
            decrypted_msg = cipher.decrypt(encrypted_msg).decode('utf-8')  # Decrypt the message and decode it to a string
            print('Dữ liệu sau khi giải mã:',decrypted_msg)    
            if (decrypted_msg == 'docbienso_dauvao') : # be176893a0d371509acbc5e10e66346c
                print('1')                
                status_camera = 1
            elif decrypted_msg == 'docbienso_dau_ra': #92f9331644ce13fa8d5e3da0e449eb24
                print('2')                
                status_camera = 2
            else:
                message = 'yeucaukhonghople' #2809fa117ce0d67b1f90ca4fb16536d0
                print('Dữ liệu gửi đến client:', message)
                mahoa_bytes = message.encode('utf-8')        
                msg = cipher.encrypt(mahoa_bytes)  # Convert the message to bytes
                print('Dữ liệu được mã hóa:', msg.hex())
                client_socket.sendall(msg.hex().encode('utf-8'))
        except ConnectionResetError:
            print('Kết nối đã bị đóng từ phía client')
            break
    is_connected = False  # Đặt lại trạng thái kết nối

receive_thread = threading.Thread(target=receive_thread, args=(client_socket,))
receive_thread.start()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
    
receive_thread.join()
