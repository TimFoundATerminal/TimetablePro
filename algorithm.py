import statistics as stats
from math import ceil
from collections import Counter
import database as db
from multiprocessing import Process


class Classes:
    """Creates all of the classes based on requirements and resources"""
    def __init__(self, database):
        print(database)
        self.db = database
        self.cls_num = 0

    def create_classes(self):
        """Central call point of the algorithm"""
        print("Called")
        yr_ids = self.db.get_all_year_ids()
        for yr_id in yr_ids:
            self._create_classes_year(yr_id)

    def _compare_existing_classes(self, yr_id, sbjt_id, req_sets_clss):
        """Compares with the classes that are already existing"""
        ex_sets_clss = tuple(self.db.get_existing_set_classes(sbjt_id, yr_id))
        set_difference = []
        for req, ext in zip(req_sets_clss, ex_sets_clss):
            set_difference.append(req - ext)
        set_difference = tuple(set_difference)
        return ex_sets_clss

    def _create_classes_year(self, yr_id):
        """Creates classes for that year"""
        ideal_class_size = round(stats.mean(self.db.get_classroom_sizes()))
        num_students = len(self.db.get_students_in_year(yr_id))
        if num_students == 0:
            return
        num_clss = ceil(num_students/ideal_class_size)
        subjects = self.db.get_subject_teachers(yr_id)
        self._create_blocks(yr_id, subjects, num_clss)

    def _create_blocks(self, yr_id, subjects, num_clss):
        """Creates blocks within the database"""
        for block_num, subject in enumerate(subjects, 1):
            self.cls_num = 0
            sbjt_id, sbjt_type, num_sbjt_tchrs = subject
            req_sets_clss = self.split_int(num_clss, ceil(num_clss/num_sbjt_tchrs))
            ex_sets_clss = tuple(self.db.get_existing_set_classes(sbjt_id, yr_id))
            self._compare_existing_classes(yr_id, sbjt_id, req_sets_clss)
            ideal_sets_clss = req_sets_clss
            self.db.create_block(self._block_name(block_num), yr_id, block_num)
            block_id = self.db.get_last_insert_rowid()
            self._create_sets(yr_id, sbjt_id, sbjt_type, ideal_sets_clss, block_id)

    def _create_sets(self, yr_id, sbjt_id, sbjt_type, ideal_sets_clss, block_id):
        """Creates sets within the database and associates them with blocks"""
        for set_num, num_classes in enumerate(ideal_sets_clss, 1):
            self.db.create_set(sbjt_id, yr_id, set_num, sbjt_type)
            set_id = self.db.get_last_insert_rowid()
            self.db.add_set_to_block(block_id, set_id)
            self._create_clss(yr_id, sbjt_id, sbjt_type, num_classes, set_id)

    def _create_clss(self, yr_id, sbjt_id, sbjt_type, num_classes, set_id):
        """Creates empty classes within the database and associates them with sets"""
        for cls in range(num_classes):
            self.cls_num += 1
            name = self._class_name(self.cls_num, yr_id, sbjt_id)
            self.db.create_empty_class(name, self.cls_num, yr_id, sbjt_id, sbjt_type)
            cls_id = self.db.get_last_insert_rowid()
            self.db.add_class_to_set(set_id, cls_id)

    def _class_name(self, i, yr_id, sbjt_id):
        """Takes class number, year and subject and generates the class name"""
        if len(str(i)) == 1:
            i = "0"+str(i)
        else:
            i = str(i)
        sbjt_code = self.db.get_subject_code(sbjt_id)
        yr_value = self.db.get_year_name(yr_id)
        return yr_value+"/"+sbjt_code+i

    @staticmethod
    def _block_name(num):
        """Converts number into character"""
        return chr(num+64)

    @staticmethod
    def _split_list(alist, wanted_parts=1):
        """Splits a list into multiple sections of as close as possible to equal length"""
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]

    @staticmethod
    def split_int(num, div):
        """Splits integer into values as close as possible to equal length"""
        remainder = num % div
        integer = num // div
        splits = []
        for i in range(div):
            splits.append(integer)
        for i in range(remainder):
            splits[i] += 1
        return tuple(splits)

    @staticmethod
    def to_matrix(list_, n):
        return [list_[i:i + n] for i in range(0, len(list_), n)]


if __name__ == '__main__':
    main_database = db.MainDatabase("Tester")
    backend = Classes(main_database)
    backend.create_classes()
