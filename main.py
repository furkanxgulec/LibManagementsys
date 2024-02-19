import os
import pandas as pd

class Library:
    def __init__(self):
        self.file_path = "books.txt"
        self.list_file_path = "read_list.txt"
        self.borrowed_file_path = "borrowed_books.txt"
        self.listfile = None
        self.file = None
        self.borrowed_file = None
        self.book_id_counter = 1
        self.open_files()

    def open_files(self):
        if not os.path.isfile(self.list_file_path):
            with open(self.list_file_path, "a+",  encoding="utf-8") as listfile:
                listfile.write("ID,Kitap Adı,Yazar,Yayın Yılı,Sayfa Sayısı,Okunan Sayfa,Okuma yüzdesi\n")

        if not os.path.isfile(self.file_path):
            with open(self.file_path, "a+",  encoding="utf-8") as file:
                file.write("ID,Kitap Adı,Yazar,Yayın Yılı,Sayfa Sayısı\n")

        if not os.path.isfile(self.borrowed_file_path):
            with open(self.borrowed_file_path, "a+",  encoding="utf-8") as borrowed_file:
                borrowed_file.write("ID,Kitap Adı,Ödünç Alan Kişi,TelefonNo,Planlanan İade Tarihi\n")

        self.listfile = open(self.list_file_path, "a+")
        self.file = open(self.file_path, "a+")
        self.borrowed_file = open(self.borrowed_file_path, "a+")

    def close_files(self):
        if self.listfile:
            self.listfile.close()
        if self.file:
            self.file.close()
        if self.borrowed_file:
            self.borrowed_file.close()

    def __del__(self):
        self.close_files()

    # books text içindeki sonkitabın idsini çeker
    def get_last_book_id(self):
        self.file.seek(0)
        books = self.file.read().splitlines()

        if books and books[0].startswith("ID"):
            books = books[1:]

        if books:
            last_book = books[-1]
            last_book_info = last_book.split(',')
            return int(last_book_info[0])

        return 0

    #1 Kitapları listeleme işlemini gerçekleştir
    def list_books(self):
        self.file.seek(0)
        books = self.file.read().splitlines()

        # Skip the header line
        if books and books[0].startswith("ID"):
            books = books[1:]

        for book in books:
            book_info = book.split(',')
            print(f"ID: {book_info[0]}, Kitap Adı: {book_info[1]}, Yazar: {book_info[2]}, Yayın yılı: {book_info[3]}, Sayfa sayısı: {book_info[4]}")

    #2 Kitap ekleme işlemini gerçekleştir
    def add_book(self, title, author, release_year, num_pages):
        last_book_id = self.get_last_book_id()
        book_info = f"{last_book_id + 1},{title},{author},{release_year},{num_pages}\n"
        self.file.write(book_info)
        self.file.flush()
        print(f"{title} kütüphaneye eklendi. ID: {last_book_id + 1}")

    #3 seçilen kitabı sil
    def remove_book(self, title):
        self.file.seek(0)
        books = self.file.read().splitlines()

        new_books = []
        removed = False

        for book in books:
            if title not in book:
                new_books.append(book)
            else:
                removed = True

        if removed:
            with open(self.file_path, "w") as file:
                file.write('\n'.join(new_books))

        return removed

    #4 okuma listesini listele
    def list_read_list(self):
        try:
            read_list_df = pd.read_csv(self.list_file_path, encoding="utf-8")
            print(read_list_df.to_string(index=False))
        except UnicodeDecodeError:
            print("Dosya UTF-8 formatında değil. Lütfen uygun bir format kullanın.")

    #5 okuma listesine kitap ekle
    def add_to_read_list(self, book_id):
        self.file.seek(0)
        books = self.file.read().splitlines()

        for book in books:
            book_info = book.split(',')
            if book_info[0] == book_id:
                list_info = f"{book_id},{book_info[1]},{book_info[2]},{book_info[3]},{book_info[4]},0\n"
                self.listfile.write(list_info)
                self.listfile.flush()
                print(f"Kitap ID {book_id} okuma listesine eklendi.")
                return True

        print(f"Kitap ID {book_id} kütüphanede bulunamadı.")
        return False

    #6 kitaptan kaç sayfa okunduğunu gerçekleştir
    def update_read_pages(self, book_id, pages_read):
        try:
            read_list_df = pd.read_csv(self.list_file_path)
        except pd.errors.EmptyDataError:
            print("Okuma listesi boş.")
            return False

        book_info = read_list_df[read_list_df['ID'] == int(book_id)]

        if not book_info.empty:
            current_pages_read = int(book_info['Okunan Sayfa'].iloc[0])
            new_pages_read = current_pages_read + pages_read
            total_pages = int(book_info['Sayfa Sayısı'].iloc[0])
            read_percentage = (new_pages_read / total_pages) * 100

            # Güncelleme işlemi
            read_list_df.loc[read_list_df['ID'] == int(book_id), 'Okunan Sayfa'] = new_pages_read
            read_list_df.loc[read_list_df['ID'] == int(book_id), 'Okuma yüzdesi'] = read_percentage

            # Dosyaya yazma işlemi
            read_list_df.to_csv(self.list_file_path, index=False)

            print(f"Kitap ID {book_id} için {pages_read} sayfa daha eklendi.")
            return True
        else:
            print(f"Kitap ID {book_id} kütüphanede bulunamadı.")
            return False

    #7 kitabın ilerleme yüzdesini göster
    def show_progress_book(self, book_id):
        try:
            read_list_df = pd.read_csv(self.list_file_path, header=0)
            read_list_df.set_index("ID", inplace=True)
        except pd.errors.EmptyDataError:
            print("Okuma listesi boş.")
            return False

        if book_id in read_list_df.index:
            book_info = read_list_df.loc[int(book_id)]

            print(f"\nİlerleme Bilgileri - Kitap ID {book_id}")
            print(f"Kitap Adı: {book_info['Kitap Adı']}")
            print(f"Yazar: {book_info['Yazar']}")
            print(f"Yayın Yılı: {book_info['Yayın Yılı']}")
            print(f"Sayfa Sayısı: {book_info['Sayfa Sayısı']}")
            print(f"Okunan Sayfa: {book_info['Okunan Sayfa']}")
            print(f"Okuma Yüzdesi: {book_info['Okuma yüzdesi']}%")
        else:
            print(f"Kitap ID {book_id} kütüphanede bulunamadı.")


    #8 Ödünç verilen kitapları listele
    def list_borrowed_books(self):
        borrowed_books_df = pd.read_csv(self.borrowed_file_path)
        if not borrowed_books_df.empty:
            print("\n*** Ödünç Verilen Kitaplar ***")
            print(borrowed_books_df.to_string(index=False))
        else:
            print("Henüz ödünç verilen kitap bulunmamaktadır.")


    #9 kitap ödünç verme fonksiyonu, verilen kitabı ve kişi bilgilerini gir
    def borrow_book(self, book_id, borrower_name, borrower_phone, return_date):
        self.file.seek(0)
        books = self.file.read().splitlines()

        for book in books:
            book_info = book.split(',')
            if book_info[0] == book_id:
                borrowed_info = f"{book_id},{book_info[1]},{borrower_name},{borrower_phone},{return_date}\n"
                self.borrowed_file.write(borrowed_info)
                self.borrowed_file.flush()
                print(f"Kitap ID {book_id} ödünç verildi. İade tarihi: {return_date}")
                return True

        print(f"Kitap ID {book_id} kütüphanede bulunamadı.")
        return False


    # menüfonksiyonu
    def menu_call(self):
        print("\n*** MENÜ ***")
        print("1) Kitapları Listele")
        print("2) Kitap Ekle")
        print("3) Kitap Sil")
        print("4) Okuma Listesini Listele")
        print("5) Okuma Listesine Kitap Ekle")
        print("6) Okunan Sayfa Ekleyin")
        print("7) Seçilen Kitabın İlerlemesini Göster")
        print("8) Ödünç Verilen Kitapları Listele")
        print("9) Kitap Ödünç Al")
        print("11) Çıkış")

        user_choice = input("Seçiminiz (1-11): ")
        # list_books fonksiyonu çağırma
        if user_choice == "1":
            self.list_books()

        # add_book fonksiyonunu çağırma
        elif user_choice == "2":
            title = input("Kitap Adı: ")
            author = input("Yazar Adı: ")
            release_year = input("Yayın Yılı: ")
            num_pages = input("Sayfa Sayısı: ")
            self.add_book(title, author, release_year, num_pages)

        # remove_book fonksiyonunu çağırma
        elif user_choice == "3":
            title_to_remove = input("Silmek istediğiniz kitabın adını girin: ")
            if self.remove_book(title_to_remove):
                print(f"{title_to_remove} kütüphaneden silindi.")
            else:
                print(f"{title_to_remove} kütüphanede bulunamadı.")

        # list_read_list fonksiyonunu çağırma
        elif user_choice == "4":
            self.list_read_list()

        # add_to_read_list fonksiyonunu çağırma
        elif user_choice == "5":
            self.list_books()
            book_id_to_add = input("Eklemek istediğiniz kitabın ID'sini girin: ")
            self.add_to_read_list(book_id_to_add)

        # update_read_pages fonksiyonunu çağır, kitap id ve okunan sayfa sayısını gir
        elif user_choice == "6":
            self.list_read_list()
            book_id_to_update = input("Hangi kitabın okunan sayfasını eklemek istiyorsunuz? ID'yi girin: ")
            pages_read_to_add = int(input("Kaç sayfa okunduğunu girin: "))
            self.update_read_pages(book_id_to_update, pages_read_to_add)

        # show_progress_book fonksiyonun çağır ve id gir ve kitabın okunaan sayfalarını gir
        elif user_choice == "7":
            show_bookid_progress = input("İlerlemesini görmek istediğiniz kitabın ID'sini girin: ")
            self.show_progress_book(int(show_bookid_progress))

        #list_borrowed_books fonksiyonunu çağır. ödünç verilen kitapları listeler
        elif user_choice == "8":
            self.list_borrowed_books()

        #borrow_book fonksiyonunu çağırır, ödünç verilen kitap idsi girilir, kişi bilgileri ve beklenen iade tarihi bilgisi girilir.
        elif user_choice == "9":
            book_id_to_borrow = input("Ödünç almak istediğiniz kitabın ID'sini girin: ")
            borrower_name = input("Kişinin adını girin: ")
            borrower_phone = input("Kişinin Telefon no giriniz: ")
            return_date = input("Planlanan iade tarihini girin (Örn: 31-12-2023): ")
            self.borrow_book(book_id_to_borrow, borrower_name, return_date)

        elif user_choice == "11":
            print("Programdan çıkılıyor.")
            exit()
        else:
            print("Geçersiz seçim. Lütfen geçerli bir seçenek girin.")

library = Library()
asciarts = (""""/ 

#######################################################                                                                            
#   ____ _     ___  ____    _    _          _    ___  #
#  / ___| |   / _ \| __ )  / \  | |        / \  |_ _| #
# | |  _| |  | | | |  _ \ / _ \ | |       / _ \  | |  #
# | |_| | |__| |_| | |_) / ___ \| |___   / ___ \ | |  #
#  \____|_____\___/|____/_/   \_\_____| /_/   \_\___| #
#                                                     #
###########LIBRARY MANAGEMENT SYSTEM V0.1##############                                  

 """)
print(asciarts)
while True:
    choice1 = input("İşlem yapmak istiyor musunuz?[e/h]: ")
    if choice1 == "e":
        library.menu_call()

    elif choice1 == "h":
        print("Programdan çıkılıyor.")
        break
    else:
        print("Geçersiz seçim. Lütfen geçerli bir seçenek girin.")
