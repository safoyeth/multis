#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.aspectRatio = 0
		self.transformationInProgress = False
		self.controller = ControllerWidget()
		self.previewer = PreviewWidget()
		self.controller.editor.setDisabled(True)
		self.progress = QProgressBar(self)

		self.horizontalSplitter = QSplitter(self)
		self.verticalSplitter = QSplitter(self)

		self.layout = QVBoxLayout()

		self.container = QWidget()
		self.vlayout = QVBoxLayout()

		self.horizontalSplitter.setOrientation(Qt.Horizontal)
		self.horizontalSplitter.addWidget(self.controller)
		self.horizontalSplitter.addWidget(self.previewer)

		self.vlayout.addWidget(self.horizontalSplitter)
		self.container.setLayout(self.vlayout)

		self.verticalSplitter.setOrientation(Qt.Vertical)
		self.verticalSplitter.addWidget(self.container)
		self.verticalSplitter.addWidget(self.progress)

		self.layout.addWidget(self.verticalSplitter)

		self.setLayout(self.layout)

		self.controller.openButton.clicked.connect(self.addImages)
		self.controller.clearButton.clicked.connect(lambda: [self.controller.imgContainer.clear(),
															 self.controller.removeButton.setDisabled(True)])
		self.controller.imgContainer.currentItemChanged.connect(self.showPreview)
		self.controller.removeButton.clicked.connect(lambda: self.controller.imgContainer.takeItem(self.controller.imgContainer.currentRow()))
		self.controller.editor.width.valueChanged.connect(self.scalingW)
		self.controller.editor.height.valueChanged.connect(self.scalingH)
		self.controller.editor.prefixLabel.stateChanged.connect(lambda: self.controller.editor.prefix.setEnabled(True) if self.controller.editor.prefixLabel.isChecked() else
																		self.controller.editor.prefix.setDisabled(True))
		self.controller.editor.changeFormat.stateChanged.connect(lambda: self.controller.editor.format.setEnabled(True) if self.controller.editor.changeFormat.isChecked() else
																		 self.controller.editor.format.setDisabled(True))
		self.controller.editor.convertedPreview.clicked.connect(self.onPreview)
		self.controller.editor.do.clicked.connect(self.transform)
		self.progress.valueChanged.connect(self.end)

	def addImages(self):
		images = QFileDialog.getOpenFileNames(self, "Выберите изображения", "", "Файлы изображений (*.bmp *.gif *.jpg *.jpeg *.png *.ico *.ppm *.xbm *.xpm)")
		for each in images[0]:
			item = QListWidgetItem(QIcon("data/bmp.png") if each.split(".")[-1] == "bmp" or each.split(".")[-1] == "BMP" else
									   QIcon("data/gif.png") if each.split(".")[-1] == "gif" or each.split(".")[-1] == "GIF" else
									   QIcon("data/jpg.png") if each.split(".")[-1] == "jpg" or each.split(".")[-1] == "JPG" else
									   QIcon("data/jpg.png") if each.split(".")[-1] == "jpeg" or each.split(".")[-1] == "JPEG" else
									   QIcon("data/png.png") if each.split(".")[-1] == "png" or each.split(".")[-1] == "PNG" else
									   QIcon("data/pict.png"),
				 					   each, self.controller.imgContainer)
			self.controller.imgContainer.addItem(item)

	def showPreview(self, item):
		if item:
			self.controller.editor.setEnabled(True)
			self.controller.editor.prefix.setDisabled(True)
			self.controller.editor.format.setDisabled(True)
			self.controller.removeButton.setEnabled(True)
			pix = QPixmap(item.text())
			w = pix.width()
			h = pix.height()
			self.aspectRatio = float(w)/float(h)
			self.controller.editor.width.setValue(w) if not self.transformationInProgress else None
			self.controller.editor.height.setValue(h) if not self.transformationInProgress else None	
			if (pix.width() > 800 or pix.height() > 600):
				self.previewer.previewer.setPixmap(pix.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
			else:
				self.previewer.previewer.setPixmap(pix)
			
			self.previewer.name.setText("<p style='font-size: 14px;'><b>Название: " + item.text() + "</b></p>")
			self.previewer.width.setText("<p style='font-size: 14px;'><b>Оригинальная ширина: " + str(w) + " px</b></p>")
			self.previewer.height.setText("<p style='font-size: 14px;'><b>Оригинальная высота: " + str(h) + " px</b></p>")
			self.previewer.aspectRatio.setText("<p style='font-size: 14px;'><b>Соотношение сторон: " + str(self.aspectRatio) + "</b></p>")

	def scalingW(self, value):
		self.controller.editor.height.valueChanged.disconnect()
		if not self.controller.editor.aspectRatio.isChecked():
			if self.aspectRatio > 1:
				self.controller.editor.height.setValue(int(value/self.aspectRatio))
			if self.aspectRatio == 1.0:
				self.controller.editor.height.setValue(value)
		self.controller.editor.height.valueChanged.connect(self.scalingH)

	def scalingH(self, value):
		self.controller.editor.width.valueChanged.disconnect()
		if not self.controller.editor.aspectRatio.isChecked():
			if self.aspectRatio > 1:
				self.controller.editor.width.setValue(int(value*self.aspectRatio))
			if self.aspectRatio == 1.0:
				self.controller.editor.width.setValue(value)
		self.controller.editor.width.valueChanged.connect(self.scalingW)

	def onPreview(self):
		pix = QPixmap(self.controller.imgContainer.item(self.controller.imgContainer.currentRow()).text())
		ps = pix.scaled(self.controller.editor.width.value(), self.controller.editor.height.value(), 
								Qt.KeepAspectRatio if not self.controller.editor.aspectRatio.isChecked() else Qt.IgnoreAspectRatio,
								Qt.SmoothTransformation if self.controller.editor.transformTypeSmooth.isChecked() else Qt.FastTransformation)
		dlg = QDialog(self)
		dlg.setWindowTitle(self.controller.imgContainer.item(self.controller.imgContainer.currentRow()).text().split("/")[-1] + "|" + 
							str(self.controller.editor.width.value()) + "X" + str(self.controller.editor.height.value()))
		dlg.setWindowIcon(QIcon("data/preview.png"))
		layer = QHBoxLayout(dlg)
		lb = QLabel("", dlg)
		lb.setPixmap(ps)
		layer.addWidget(lb)
		dlg.setLayout(layer)
		dlg.show()

	def transform(self):
		self.transformationInProgress = True
		if not os.path.exists('converted'):
			os.mkdir('converted')
		self.progress.setRange(0, self.controller.imgContainer.count())
		for each in range(self.controller.imgContainer.count()):
			self.controller.imgContainer.setCurrentRow(each)
			self.progress.setValue(each+1)
			self.convertCurrent()
		self.transformationInProgress = False

	def convertCurrent(self):
		pix = QPixmap(self.controller.imgContainer.item(self.controller.imgContainer.currentRow()).text())
		filename = self.controller.imgContainer.item(self.controller.imgContainer.currentRow()).text().split("/")[-1]
		name = filename.split(".")[0]
		ext = filename.split(".")[-1].upper()
		if not self.controller.editor.changeFormat.isChecked():
			if not self.controller.editor.prefixLabel.isChecked():
				fileToBeWritten = QFile("converted/" + filename)
				fileToBeWritten.open(QIODevice.WriteOnly)
				ps = pix.scaled(self.controller.editor.width.value(), self.controller.editor.height.value(), 
								Qt.KeepAspectRatio if not self.controller.editor.aspectRatio.isChecked() else Qt.IgnoreAspectRatio,
								Qt.SmoothTransformation if self.controller.editor.transformTypeSmooth.isChecked() else Qt.FastTransformation)
				ps.save(fileToBeWritten, ext)
				fileToBeWritten.close()
			else:
				if not self.controller.editor.prefix.text() == "":
					fileToBeWritten = QFile("converted/" + self.controller.editor.prefix.text() + filename)
					fileToBeWritten.open(QIODevice.WriteOnly)
					ps = pix.scaled(self.controller.editor.width.value(), self.controller.editor.height.value(), 
									Qt.KeepAspectRatio if not self.controller.editor.aspectRatio.isChecked() else Qt.IgnoreAspectRatio,
									Qt.SmoothTransformation if self.controller.editor.transformTypeSmooth.isChecked() else Qt.FastTransformation)
					ps.save(fileToBeWritten, ext)
					fileToBeWritten.close()
				else:
					QMessageBox.warning(self, "Multis", "Пожалуйста, добавьте префикс!")
		else:
			if not self.controller.editor.prefixLabel.isChecked():
				fileToBeWritten = QFile("converted/" + name + "." + self.controller.editor.format.currentText().lower())
				fileToBeWritten.open(QIODevice.WriteOnly)
				ps = pix.scaled(self.controller.editor.width.value(), self.controller.editor.height.value(), 
								Qt.KeepAspectRatio if not self.controller.editor.aspectRatio.isChecked() else Qt.IgnoreAspectRatio,
								Qt.SmoothTransformation if self.controller.editor.transformTypeSmooth.isChecked() else Qt.FastTransformation)
				ps.save(fileToBeWritten, self.controller.editor.format.currentText())
				fileToBeWritten.close()
			else:
				if not self.controller.editor.prefix.text() == "":
					fileToBeWritten = QFile("converted/" + self.controller.editor.prefix.text() + name + "." + self.controller.editor.format.currentText().lower())
					fileToBeWritten.open(QIODevice.WriteOnly)
					ps = pix.scaled(self.controller.editor.width.value(), self.controller.editor.height.value(), 
									Qt.KeepAspectRatio if not self.controller.editor.aspectRatio.isChecked() else Qt.IgnoreAspectRatio,
									Qt.SmoothTransformation if self.controller.editor.transformTypeSmooth.isChecked() else Qt.FastTransformation)
					ps.save(fileToBeWritten, name + self.controller.editor.format.currentText())
					fileToBeWritten.close()
				else:
					QMessageBox.warning(self, "Multis", "Пожалуйста, добавьте префикс!")

	def end(self, value):
		if value == self.progress.maximum():
			self.progress.setValue(0)
			QMessageBox.information(self, "Multis", "Конвертация успешно завершена!")
			os.startfile("converted")



class PreviewWidget(QWidget):
	def __init__(self):
		super(PreviewWidget, self).__init__()
		self.layer = QGridLayout()
		self.previewer = QLabel("", self)
		self.name = QLabel("", self)
		self.width = QLabel("", self)
		self.height = QLabel("", self)
		self.aspectRatio = QLabel("", self)

		self.layer.addWidget(self.previewer, 0, 0, 40, 50)
		self.layer.addWidget(self.name, 41, 0, 1, 50)
		self.layer.addWidget(self.width, 42, 0, 1, 50)
		self.layer.addWidget(self.height, 43, 0, 1, 50)
		self.layer.addWidget(self.aspectRatio, 44, 0, 1, 50)

		self.setLayout(self.layer)

class ControllerWidget(QWidget):
	def __init__(self):
		super(ControllerWidget, self).__init__()
		self.layer = QGridLayout()
		self.editor = EditorWidget()

		self.openButton = QPushButton(QIcon("data/add.png"), "Добавить изображения", self)
		self.removeButton = QPushButton(QIcon("data/remove.png"), "Удалить из списка", self)
		self.clearButton = QPushButton(QIcon("data/delete.png"), "Очистить список", self)
		self.imgContainer = QListWidget(self)

		self.removeButton.setDisabled(True)

		self.layer.addWidget(self.imgContainer, 0, 0, 20, 5)
		self.layer.addWidget(self.openButton, 0, 6, 1, 1)
		self.layer.addWidget(self.removeButton, 1, 6, 1, 1)
		self.layer.addWidget(self.clearButton, 2, 6, 1, 1)
		self.layer.addWidget(self.editor, 3, 6, 1, 1)

		self.setLayout(self.layer)

class EditorWidget(QWidget):
	def __init__(self):
		super(EditorWidget, self).__init__()
		self.layer = QGridLayout()

		self.widthLabel = QLabel("Ширина, px", self)
		self.width = QSpinBox(self)
		self.width.setRange(1, 10000)
		self.widthLabel.setBuddy(self.width)
		self.heightLabel = QLabel("Высота, px", self)
		self.height = QSpinBox(self)
		self.height.setRange(1, 10000)
		self.heightLabel.setBuddy(self.height)
		self.aspectRatio = QCheckBox("Игнорировать соотношение сторон", self)
		self.transformTypeFast = QRadioButton("Быстрая трансформация (без сглаживания)", self)
		self.transformTypeSmooth = QRadioButton("Использовать сглаживание (биленейный фильтр)", self)
		self.transformTypeSmooth.setChecked(True)
		self.prefixLabel = QCheckBox("Использовать префикс для сконвертированных файлов", self)
		self.prefix = QLineEdit(self)
		self.changeFormat = QCheckBox("Преобразовать в:", self)
		self.format = QComboBox(self)
		self.format.addItems(["BMP", "JPG", "JPEG", "PNG", "PPM", "XBM", "XPM"])
		self.convertedPreview = QPushButton(QIcon("data/preview.png"), "Предварительный просмотр", self)
		self.do = QPushButton(QIcon("data/shape.png"), "Конвертировать!", self)

		self.layer.addWidget(self.widthLabel, 0, 0)
		self.layer.addWidget(self.width, 0, 1)
		self.layer.addWidget(self.aspectRatio, 1, 0)
		self.layer.addWidget(self.heightLabel, 2, 0)
		self.layer.addWidget(self.height, 2, 1)
		self.layer.addWidget(self.transformTypeFast, 3, 0, 1, 2)
		self.layer.addWidget(self.transformTypeSmooth, 4, 0, 1, 2)		
		self.layer.addWidget(self.prefixLabel, 5, 0, 1, 2)
		self.layer.addWidget(self.prefix, 6, 0, 1, 2)
		self.layer.addWidget(self.changeFormat, 7, 0, 1, 2)
		self.layer.addWidget(self.format, 8, 0, 1, 2)
		self.layer.addWidget(self.convertedPreview, 9, 0, 1, 2)
		self.layer.addWidget(self.do, 10, 0, 1, 2)

		self.setLayout(self.layer)

def main():
	application = QApplication(sys.argv)
	application.setStyle("fusion")
	window = Window()
	window.setWindowTitle("Multis")
	window.setWindowIcon(QIcon("data/shape.png"))
	window.showMaximized()
	sys.exit(application.exec_())

if __name__ == "__main__":
	main()