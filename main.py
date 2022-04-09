"""generator haseł z możliwością zapamietywania i zapisywania haseł"""

import sys
import random
import string
import shelve
import requests
from hashlib import sha1
import pyperclip
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot
from PySide6.QtCore import Signal
from PySide6.QtCore import QSize

# minimalna długość hasła
MIN_PASSWORD_LENGTH = 10
# ścieżka do pliku z danymi
FILEPATH = r'C:\Users\kucha\Kodowanie\Nauka\generator\data'

# klasa okna głównego aplikacji
class GeneratorHasel(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        loader = QUiLoader()
        self.window = loader.load(r"C:\Users\kucha\Kodowanie\Nauka\generator\window.ui", self)
        self.password = []

        # tworzenie obiektów grafiki
        pix_copy = QPixmap(r'C:\Users\kucha\Kodowanie\Nauka\generator\copy.png')
        self.window.kopiujBtn.setIcon(QIcon(pix_copy))
        self.window.kopiujBtn.setIconSize(QSize(30, 30))

        # przypisywanie akcji do buttona
        self.window.pushButton.clicked.connect(self.generuj_haslo)
        self.window.kopiujBtn.clicked.connect(self.kopiuj_haslo)
        self.window.otworzBtn.clicked.connect(self.otworz)
        self.window.zapiszBtn.clicked.connect(self.zapisz)

        self.window.show()

    def otworz(self):
        # otwiera okno do pobierania haseł
        self.otworzWindow = Otworz(FILEPATH)
        self.otworzWindow.setWindowTitle('Pobieranie haseł')
        self.otworzWindow.show()

    def zapisz(self):
        # otwiera okno do zapisu haseł
        if len(self.password) > 7:
            self.zapiszWindow = Zapisz(self.password, FILEPATH)
            self.zapiszWindow.setWindowTitle("Zapisywanie")
            self.zapiszWindow.show()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle('Info')
            msg.setText('Nie wygenerowano hasła, czy chcesz zapisać własne?')
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            k = msg.exec()
            if k == 1024:
                self.zapiszWindow = Zapisz('', FILEPATH)
                self.zapiszWindow.setWindowTitle("Zapisywanie")
                self.zapiszWindow.show()

    def generuj_haslo(self):
        # metoda generująca hasło zgodnie z podaną liczbą znaków:
        # wielkie litery
        try:
            uppercase_letters = int(self.window.lineEdit_2.text())
        except ValueError:
            uppercase_letters = 0
        # małe litery
        try:
            lowercase_letters = int(self.window.lineEdit_3.text())
        except ValueError:
            lowercase_letters = 0
        # cyfry
        try:
            digits = int(self.window.lineEdit.text())
        except ValueError:
            digits = 0
        # znaki specjalne
        try:
            special_characters = int(self.window.lineEdit_4.text())
        except ValueError:
            special_characters = 0
        #długość hasła
        password_length = uppercase_letters + lowercase_letters + digits + special_characters
        password = []

        # sprawdzanie warunku minimalnej długości hasła
        if password_length < MIN_PASSWORD_LENGTH:
            self.window.label_6.setText("Za krótkie hasło, podaj więciej znaków")
        else:
            self.window.label_6.setText(f"Twoje hasło składa się z {password_length} znaków:")

            for _ in range(password_length):
                if uppercase_letters > 0:
                    password.append(random.choice(string.ascii_uppercase))
                    uppercase_letters -= 1
                if lowercase_letters > 0:
                    password.append(random.choice(string.ascii_lowercase))
                    lowercase_letters -= 1
                if special_characters > 0:
                    password.append(random.choice(string.punctuation))
                    special_characters -= 1
                if digits > 0:
                    password.append(random.choice(string.digits))
                    digits -= 1

            random.shuffle(password)
            self.password = "".join(password)
            if self.validate_password(self.password):
                self.window.label_password.setText(self.password)
            else:
                self.window.label_6.setText("Wygeneruj jeszcze raz hasło")

    def validate_password(self, password):
        """sprawdza czy hasło wyciekło

        Args:
            password (str): hasło do sprawdzenia

        Returns:
            bool: True jeżeli hasło nie wyciekło
        """
        password_hash = sha1(password.encode('utf-8')).hexdigest().upper()
        url = 'https://api.pwnedpasswords.com/range/' + f'{password_hash[:5]}'
        response = requests.get(url).text.split()
        return bool(password_hash[5:] not in [hash.partition(':')[0] for hash in response])

    def kopiuj_haslo(self):
        pyperclip.copy(self.password) if len(self.password) > 7 \
            else self.window.label_6.setText("Brak wygenerowanego hasła")

# zpaisywanie haseł do pamięci
class Zapisz(QWidget):
    zapisano_haslo = Signal()

    def __init__(self, password, filepath):
        super().__init__()
        self.password = password
        self.path = filepath
        loader = QUiLoader()
        self.window = loader.load(r"C:\Users\kucha\Kodowanie\Nauka\generator\zapisz.ui", self)
        self.window.passwordLine.setText(self.password)
        self.window.zapiszButton.clicked.connect(self.zapisz_haslo)
        self.window.zamknijButton.clicked.connect(self.zamknij)

    def name_exist_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setWindowTitle('Uwaga')
        msg.setText('Ta pozycja już istnieje, czy chcesz ją nadpisać?')
        return msg.exec()

    def save_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Info')
        msg.setText('Zapisano hasło')
        self.zapisano_haslo.emit()
        msg.exec()

    def fill_empty_msg(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle('Info')
        msg.setText('Uzupełnij puste pola')
        msg.exec()

    def zapisz_haslo(self):
        # zapisuje nowe hasło wraz z loginem i nazwą w pamięci (plik: data)
        hasla = shelve.open(self.path)
        if self.window.nameLine.text() in list(hasla.keys()):
            k = self.name_exist_msg()
            if k == 1024:
                if len(self.window.loginLine.text()) > 0 \
                    and len(self.window.passwordLine.text()) > 0:
                    hasla[self.window.nameLine.text()] = self.window.loginLine.text(),\
                         self.window.passwordLine.text()
                    hasla.close()
                    self.close()
                    self.save_msg()
                else:
                    self.fill_empty_msg()
            else:
                hasla.close()
                self.close()
        elif len(self.window.nameLine.text()) > 0 and len(self.window.loginLine.text()) > 0\
             and len(self.window.passwordLine.text()) > 0:
            hasla[self.window.nameLine.text()] = self.window.loginLine.text(),\
                 self.window.passwordLine.text()
            hasla.close()
            self.save_msg()
            self.close()
        else:
            self.fill_empty_msg()

    def zamknij(self):
        self.close()

# pobieranie haseł z pamięci
class Otworz(QWidget):
    def __init__(self, filepath=str):
        super().__init__()
        self.path = filepath
        loader = QUiLoader()
        self.window = loader.load(r"C:\Users\kucha\Kodowanie\Nauka\generator\otworz.ui", self)

        # tworzenie obiektów grafiki
        pix_copy = QPixmap(r'C:\Users\kucha\Kodowanie\Nauka\generator\copy.png')
        self.window.kopiujBtn1.setIcon(QIcon(pix_copy))
        self.window.kopiujBtn1.setIconSize(QSize(30, 30))
        self.window.kopiujBtn2.setIcon(QIcon(pix_copy))
        self.window.kopiujBtn2.setIconSize(QSize(30, 30))

        # przypisywanie funkcji do przycisków i list
        self.window.listWidget.clicked.connect(self.wybierz_haslo)
        self.window.kopiujBtn1.clicked.connect(self.kopiuj_login)
        self.window.kopiujBtn2.clicked.connect(self.kopiuj_haslo)
        self.window.usunBtn.clicked.connect(self.usun_haslo)
        self.window.dodajBtn.clicked.connect(self.dodaj_haslo)

        self.laduj_baze()

    def usun_haslo(self):
        # usuwa wybraną pozycję z listy haseł
        item = self.window.listWidget.currentItem().text()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setWindowTitle('Uwaga')
        msg.setText(f'Czy chcesz usunąć: \n  {item} ?')
        k = msg.exec()
        if  k == 1024:
            hasla = shelve.open(self.path)
            del hasla[item]
            hasla.close()
            self.laduj_baze()

    @Slot()
    def dodaj_haslo(self):
        self.zapiszWindow = Zapisz('', FILEPATH)
        self.zapiszWindow.setWindowTitle("Zapisywanie")
        self.zapiszWindow.zapisano_haslo.connect(self.laduj_baze)
        self.zapiszWindow.show()

    def kopiuj_login(self):
        pyperclip.copy(self.window.label_login.text())

    def kopiuj_haslo(self):
        pyperclip.copy(self.window.label_password.text())

    def laduj_baze(self):
        # ładuje baze zapisanych haseł do widgetu listWidget
        self.window.listWidget.clear()
        hasla = shelve.open(self.path)
        names_number = 0
        for i, key in enumerate(hasla.keys()):
            names_number = 1 + i
            self.window.listWidget.insertItem(i, key)
        hasla.close()
        self.window.label_lista.setText(f'Lista zapisanych haseł:   {names_number}')

    def wybierz_haslo(self):
        item = self.window.listWidget.currentItem().text()
        haslo = shelve.open(self.path)
        self.window.label_login.setText(str(haslo[item][0]))
        self.window.label_password.setText(str(haslo[item][1]))
        haslo.close()

if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = GeneratorHasel()
    sys.exit(app.exec())
