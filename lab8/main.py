import psycopg2
import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget,
                             QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Schedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_schedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="bot_db",
                                     user="postgres",
                                     password="Inever23",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_schedule_tab(self):
        self.schedule_tab = QWidget()
        self.tabs.addTab(self.schedule_tab, "Расписание")
        days = {
            'Понедельник': 1,
            'Вторник': 2,
            'Среда': 3,
            'Четверг': 4,
            'Пятница': 5}

        day_tab = QTabWidget(self)

        for i in days:
            day_tab.addTab(self._create_day_table(i.upper()), i)
        day_tab_layout = QVBoxLayout()
        day_tab_layout.addWidget(day_tab)
        self.schedule_tab.setLayout(day_tab_layout)

    def _create_day_table(self, day):
        if day == 'ПОНЕДЕЛЬНИК':
            day = 1
        elif day == 'ВТОРНИК':
            day = 2
        elif day == 'СРЕДА':
            day = 3
        elif day == 'ЧЕТВЕРГ':
            day = 4
        elif day == 'ПЯТНИЦА':
            day = 5
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(["id", "week", "day", "subject", "room_number",
                                         "start_time", "teacher", "", ""])
        self._update_day_table(table, day)
        return table

    def _update_day_table(self, table, day):
        self.cursor.execute(f"SELECT * FROM bot.timetable WHERE day = " + str(day) +
                            f"ORDER BY timetable.id")
        records = list(self.cursor.fetchall())

        table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            ed_sql = "UPDATE bot.timetable SET week=%s, day=%s, subject=%s, room_number=%s," \
                     " start_time=%s, teacher=%s WHERE id=%s"
            delButton = QPushButton("Delete")
            del_sql = "DELETE FROM bot.timetable WHERE id=%s"
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setItem(i, 2,
                          QTableWidgetItem(str(r[2])))
            table.setItem(i, 3,
                          QTableWidgetItem(str(r[3])))
            table.setItem(i, 4,
                          QTableWidgetItem(str(r[4])))
            table.setItem(i, 5,
                          QTableWidgetItem(str(r[5])))
            table.setItem(i, 6,
                          QTableWidgetItem(str(r[6])))
            table.setCellWidget(i, 7, editButton)
            table.setCellWidget(i, 8, delButton)

            editButton.clicked.connect(
                lambda _, num=i, tabl=table, edit=True, sql=ed_sql, tab="bot.timetable":
                self._change_from_table(num, tabl, edit, sql, tab))
            delButton.clicked.connect(
                lambda _, num=i, tabl=table, edit=False, sql=del_sql, tab="bot.timetable":
                self._change_from_table(num, tabl, edit, sql, tab))

        addButton = QPushButton("Add")
        add_sql = "INSERT INTO bot.timetable VALUES (%s, %s, %s, %s, %s, %s, %s)"
        addButton.clicked.connect(
            lambda _, num=len(records), tabl=table, sql=add_sql, tab="bot.timetable": self._add_row(num, tabl, sql, tab))
        table.setCellWidget(len(records), 7, addButton)
        table.resizeRowsToContents()

    def _create_teachers_tab(self):
        self.teachers = QWidget()
        self.tabs.addTab(self.teachers, "Преподаватели")
        table = QTableWidget(self)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["id", "full_name", "subject", "", ""])

        teachers_tab_layout = QVBoxLayout()
        teachers_tab_layout.addWidget(table)

        self._update_teachers_tab(table)
        self.teachers.setLayout(teachers_tab_layout)

    def _update_teachers_tab(self, table):
        self.cursor.execute(f"SELECT * FROM bot.teacher ORDER BY teacher.id")
        records = list(self.cursor.fetchall())

        table.setRowCount(len(records) + 1)

        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            ed_sql = "UPDATE bot.teacher SET full_name=%s, subject=%s WHERE id=%s"
            delButton = QPushButton("Delete")
            del_sql = "DELETE FROM bot.teacher WHERE id=%s"
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setItem(i, 2,
                          QTableWidgetItem(str(r[2])))
            table.setCellWidget(i, 3, editButton)
            table.setCellWidget(i, 4, delButton)

            editButton.clicked.connect(
                lambda _, num=i, tabl=table, edit=True, sql=ed_sql, tab="bot.teacher":
                self._change_from_table(num, tabl, edit, sql, tab))
            delButton.clicked.connect(
                lambda _, num=i, tabl=table, edit=False, sql=del_sql, tab="bot.teacher":
                self._change_from_table(num, tabl, edit, sql, tab))
        addButton = QPushButton("Add")
        add_sql = "INSERT INTO bot.teacher VALUES (%s, %s, %s)"
        addButton.clicked.connect(
            lambda _, num=len(records), tabl=table, sql=add_sql, tab="bot.teacher": self._add_row(num, tabl, sql, tab))
        table.setCellWidget(len(records), 3, addButton)
        table.resizeRowsToContents()

    def _create_subjects_tab(self):
        self.subjects = QWidget()
        self.tabs.addTab(self.subjects, "Предметы")
        table = QTableWidget(self)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["id", "name", "", ""])

        subjects_tab_layout = QVBoxLayout()
        subjects_tab_layout.addWidget(table)

        self._update_subjects_tab(table)
        self.subjects.setLayout(subjects_tab_layout)

    def _update_subjects_tab(self, table):
        self.cursor.execute(f"SELECT * FROM bot.subject")
        records = list(self.cursor.fetchall())
        table.setRowCount(len(records) + 1)
        for i, r in enumerate(records):
            r = list(r)
            editButton = QPushButton("Edit")
            delButton = QPushButton("Delete")
            table.setItem(i, 0,
                          QTableWidgetItem(str(r[0])))
            table.setItem(i, 1,
                          QTableWidgetItem(str(r[1])))
            table.setCellWidget(i, 2, editButton)
            table.setCellWidget(i, 3, delButton)
            editButton.clicked.connect(
                lambda _, num=i, tabl=table, old=r[0]: self._change_subjects(num, table, old))
            delButton.clicked.connect(
                lambda _, num=i, tabl=table: self._delete_subjects(num, table))

        add_sql = "INSERT INTO bot.subject VALUES (%s, %s)"
        addButton = QPushButton("Add")
        addButton.clicked.connect(
            lambda _, num=len(records), tabl=table, sql=add_sql, tab='bot.subject': self._add_row(num, tabl, sql, tab))
        table.setCellWidget(len(records), 2, addButton)
        table.resizeRowsToContents()

    def _change_subjects(self, rowNum, table, old):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute(f"SELECT * FROM bot.teacher WHERE subject=%s", (old,))
            records = list(self.cursor.fetchall())
            self.cursor.execute("DELETE FROM bot.teacher where id=%s", (old,))
            self.cursor.execute("UPDATE bot.subject SET name=%s WHERE id=%s", (row[0], old))
            for e in records:
                r = list(e)
                r[2] = row[0]
                self.cursor.execute("INSERT INTO bot.teacher VALUES (%s, %s, %s)", tuple(r))
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _delete_subjects(self, rowNum, table):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute(f"SELECT * FROM bot.teacher WHERE subject=%s", (row[0],))
            records = list(self.cursor.fetchall())
            for e in records:
                self.cursor.execute("DELETE FROM bot.timetable where teacher=%s", (e[0],))
            self.cursor.execute("DELETE FROM bot.teacher where subject=%s", (row[0],))
            self.cursor.execute("DELETE FROM bot.subject where id=%s", (row[0],))
            self.conn.commit()
            table.setRowCount(0)
            self._update_subjects_tab(table)
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _add_row(self, rowNum, table, sql, tab):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        try:
            print(row)
            if tab == 'bot.timetable':
                self.cursor.execute(f"SELECT  MAX(id) FROM bot.timetable")
                max_id = self.cursor.fetchone()[0] + 1
                if row[0] == '' or row[0] is None or int(row[0]) < max_id:
                    row[0] = max_id
                self.cursor.execute(sql, (tuple(row)))
                self.conn.commit()
                table.setRowCount(0)
                self._update_day_table(table, row[2])
            elif tab == 'bot.teacher':
                print(row)
                self.cursor.execute(f"SELECT  MAX(id) FROM bot.teacher")
                max_id = self.cursor.fetchone()[0] + 1
                if row[0] == '' or row[0] is None or int(row[0]) < max_id:
                    row[0] = max_id
                self.cursor.execute(sql, (tuple(row)))
                self.conn.commit()
                table.setRowCount(0)
                self._update_teachers_tab(table)
            elif tab == 'bot.subject':
                self.cursor.execute(sql, (tuple(row)))
                self.conn.commit()
                table.setRowCount(0)
                self._update_subjects_tab(table)
        except Exception as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
            self._connect_to_db()

    def _change_from_table(self, rowNum, table, edit, sql, tab):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rowNum, i).text())
            except:
                row.append(None)
        row.append(row[0])
        row = row[1:]
        if edit:
            try:
                print(row)
                print(rowNum)
                self.cursor.execute(sql, (tuple(row)))
                self.conn.commit()
            except Exception as e:
                QMessageBox.about(self, "Error", str(e))
                self._connect_to_db()
        else:
            try:
                if tab == 'bot.timetable':
                    print(row)
                    self.cursor.execute(sql, (row[-1],))
                    self.conn.commit()
                    table.setRowCount(0)
                    self._update_day_table(table, row[1])
                elif tab == 'bot.teacher':
                    print(row)
                    self.cursor.execute("DELETE FROM bot.timetable where teacher=%s", (row[-1],))
                    self.cursor.execute(sql, (row[-1],))
                    self.conn.commit()
                    table.setRowCount(0)
                    self._update_teachers_tab(table)
            except Exception as e:
                print(e)
                QMessageBox.about(self, "Error", str(e))
                self._connect_to_db()

    def _update(self):
        self.tabs.removeTab(0)
        self.tabs.removeTab(0)
        self.tabs.removeTab(0)
        self._create_schedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())


