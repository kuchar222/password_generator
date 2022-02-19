import shelve
import sys
import random
import string
import pyperclip
import shelve
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Slot, QSize

# minimalna długość hasła
MIN_PASSWORD_LENGTH = 8

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

    @Slot()
    def otworz(self):
        # otwiera okno do pobierania haseł
        pass

    @Slot()
    def zapisz(self):
        # otwiera okno do zapisu haseł
        print('test')
        if len(self.password) > 7:
            self.zapiszWindow = Zapisz(self.password)
            self.zapiszWindow.setWindowTitle("Zapisywanie")
            self.zapiszWindow.show()
        else:
            self.window.label_6.setText("Brak wygenerowanego hasła")
       
    @Slot()
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
            self.window.label_password.setText(self.password)

    @Slot()
    def kopiuj_haslo(self):
        pyperclip.copy(self.password) if len(self.password) > 7 else self.window.label_6.setText("Brak wygenerowanego hasła")

# zpaisywanie haseł do pamięci
class Zapisz(QWidget):
    def __init__(self, password):
        super().__init__()
        self.password = password
        loader = QUiLoader()
        self.window = loader.load(r"C:\Users\kucha\Kodowanie\Nauka\generator\zapisz.ui", self)
        self.window.passwordLine.setText(self.password)

        self.window.zapiszButton.clicked.connect(self.zapisz_haslo)
        self.window.zamknijButton.clicked.connect(self.zamknij)
    
    @Slot()
    def zapisz_haslo(self):
        # zapisuje nowe hasło wraz zloginem i nazwą w pamięci (plik: data)
        hasla = shelve.open(r'C:\Users\kucha\Kodowanie\Nauka\generator\data')
        if self.window.nameLine.text() in list(hasla.keys()):
            # TODO komunikat - taka pozycja już istnieje, czy chcesz ją zastąpić? 
            # utworzyć okno z wyborem tak - nie
            print('taka pozycja już istnieje, czy chcesz ją zastąpić?')
        elif len(self.window.nameLine.text()) > 0 and len(self.window.loginLine.text()) > 0:
            hasla[self.window.nameLine.text()] = self.window.loginLine.text(), self.password
            print('zapisano hasło')
        else:
            # TODO komunikat - uzupełnij puste pola
            
            print('uzupełnij puste pola')
        hasla.close()   

    @Slot()
    def zamknij(self):
        self.destroy()

# pobieranie haseł z pamięci
class Otworz(QWidget):
    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    window = GeneratorHasel()
    
    sys.exit(app.exec())