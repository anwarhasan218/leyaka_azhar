# -*- coding: utf-8 -*-
"""
نظام التقييم للمشروع القومي للياقة البدنية
"""

import json
from datetime import datetime

class FitnessTest:
    """فئة اختبار اللياقة البدنية"""
    
    def __init__(self, test_name, max_score, description=""):
        self.test_name = test_name
        self.max_score = max_score
        self.description = description
        self.results = []
    
    def add_result(self, student_id, score, notes=""):
        """إضافة نتيجة اختبار"""
        result = {
            'student_id': student_id,
            'score': score,
            'notes': notes,
            'date': datetime.now().isoformat(),
            'percentage': (score / self.max_score) * 100
        }
        self.results.append(result)
        return result
    
    def get_average_score(self):
        """حساب متوسط الدرجات"""
        if not self.results:
            return 0
        total_score = sum(r['score'] for r in self.results)
        return total_score / len(self.results)
    
    def get_top_performers(self, limit=10):
        """الحصول على أفضل الأداء"""
        sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)
        return sorted_results[:limit]
    
    def export_results(self, filename):
        """تصدير النتائج إلى ملف JSON"""
        data = {
            'test_name': self.test_name,
            'max_score': self.max_score,
            'description': self.description,
            'results': self.results,
            'statistics': {
                'total_participants': len(self.results),
                'average_score': self.get_average_score(),
                'top_score': max(r['score'] for r in self.results) if self.results else 0,
                'lowest_score': min(r['score'] for r in self.results) if self.results else 0
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename

class FitnessTestSuite:
    """مجموعة اختبارات اللياقة البدنية"""
    
    def __init__(self):
        self.tests = {}
        self.students = {}
    
    def add_test(self, test_id, test_name, max_score, description=""):
        """إضافة اختبار جديد"""
        self.tests[test_id] = FitnessTest(test_name, max_score, description)
        return self.tests[test_id]
    
    def add_student(self, student_id, name, gender, education_level, institute):
        """إضافة طالب جديد"""
        self.students[student_id] = {
            'name': name,
            'gender': gender,
            'education_level': education_level,
            'institute': institute,
            'tests': {}
        }
    
    def record_test_result(self, test_id, student_id, score, notes=""):
        """تسجيل نتيجة اختبار"""
        if test_id not in self.tests:
            raise ValueError(f"Test {test_id} not found")
        
        if student_id not in self.students:
            raise ValueError(f"Student {student_id} not found")
        
        # تسجيل النتيجة في الاختبار
        result = self.tests[test_id].add_result(student_id, score, notes)
        
        # تسجيل النتيجة في ملف الطالب
        self.students[student_id]['tests'][test_id] = result
        
        return result
    
    def get_student_performance(self, student_id):
        """الحصول على أداء الطالب"""
        if student_id not in self.students:
            return None
        
        student = self.students[student_id]
        performance = {
            'student_info': student,
            'test_results': student['tests'],
            'total_tests': len(student['tests']),
            'average_score': 0,
            'total_score': 0
        }
        
        if student['tests']:
            total_score = sum(r['score'] for r in student['tests'].values())
            performance['total_score'] = total_score
            performance['average_score'] = total_score / len(student['tests'])
        
        return performance
    
    def get_institute_performance(self, institute_name):
        """الحصول على أداء المعهد"""
        institute_students = [
            student_id for student_id, student in self.students.items()
            if student['institute'] == institute_name
        ]
        
        if not institute_students:
            return None
        
        total_score = 0
        total_tests = 0
        
        for student_id in institute_students:
            student_performance = self.get_student_performance(student_id)
            if student_performance:
                total_score += student_performance['total_score']
                total_tests += student_performance['total_tests']
        
        return {
            'institute_name': institute_name,
            'total_students': len(institute_students),
            'total_tests': total_tests,
            'average_score': total_score / total_tests if total_tests > 0 else 0,
            'students': institute_students
        }
    
    def get_education_level_performance(self, education_level):
        """الحصول على أداء المرحلة التعليمية"""
        level_students = [
            student_id for student_id, student in self.students.items()
            if student['education_level'] == education_level
        ]
        
        if not level_students:
            return None
        
        total_score = 0
        total_tests = 0
        
        for student_id in level_students:
            student_performance = self.get_student_performance(student_id)
            if student_performance:
                total_score += student_performance['total_score']
                total_tests += student_performance['total_tests']
        
        return {
            'education_level': education_level,
            'total_students': len(level_students),
            'total_tests': total_tests,
            'average_score': total_score / total_tests if total_tests > 0 else 0,
            'students': level_students
        }
    
    def generate_report(self, report_type="comprehensive"):
        """إنشاء تقرير شامل"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_students': len(self.students),
            'total_tests': len(self.tests),
            'test_summaries': {},
            'institute_performance': {},
            'education_level_performance': {},
            'top_performers': {}
        }
        
        # ملخص الاختبارات
        for test_id, test in self.tests.items():
            report['test_summaries'][test_id] = {
                'name': test.test_name,
                'max_score': test.max_score,
                'participants': len(test.results),
                'average_score': test.get_average_score(),
                'top_performers': test.get_top_performers(5)
            }
        
        # أداء المعاهد
        institutes = set(student['institute'] for student in self.students.values())
        for institute in institutes:
            performance = self.get_institute_performance(institute)
            if performance:
                report['institute_performance'][institute] = performance
        
        # أداء المراحل التعليمية
        education_levels = set(student['education_level'] for student in self.students.values())
        for level in education_levels:
            performance = self.get_education_level_performance(level)
            if performance:
                report['education_level_performance'][level] = performance
        
        # أفضل الأداء
        all_students_performance = []
        for student_id in self.students:
            performance = self.get_student_performance(student_id)
            if performance and performance['total_tests'] > 0:
                all_students_performance.append({
                    'student_id': student_id,
                    'student_name': performance['student_info']['name'],
                    'institute': performance['student_info']['institute'],
                    'education_level': performance['student_info']['education_level'],
                    'average_score': performance['average_score'],
                    'total_tests': performance['total_tests']
                })
        
        # ترتيب حسب متوسط الدرجات
        all_students_performance.sort(key=lambda x: x['average_score'], reverse=True)
        report['top_performers'] = all_students_performance[:20]
        
        return report
    
    def export_report(self, filename, report_type="comprehensive"):
        """تصدير التقرير إلى ملف JSON"""
        report = self.generate_report(report_type)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filename

# أمثلة على الاستخدام
if __name__ == "__main__":
    # إنشاء مجموعة اختبارات
    test_suite = FitnessTestSuite()
    
    # إضافة اختبارات
    test_suite.add_test("test1", "اختبار الجري 100 متر", 15, "اختبار سرعة الجري")
    test_suite.add_test("test2", "اختبار القفز الطويل", 10, "اختبار القوة الانفجارية")
    test_suite.add_test("test3", "اختبار الجلوس والوقوف", 20, "اختبار التحمل العضلي")
    
    # إضافة طلاب
    test_suite.add_student("S001", "أحمد محمد", "male", "primary", "معهد الأزهر الابتدائي")
    test_suite.add_student("S002", "فاطمة علي", "female", "primary", "معهد الأزهر الابتدائي")
    test_suite.add_student("S003", "محمد أحمد", "male", "middle", "معهد الأزهر الإعدادي")
    
    # تسجيل نتائج الاختبارات
    test_suite.record_test_result("test1", "S001", 12, "أداء جيد")
    test_suite.record_test_result("test2", "S001", 8, "أداء ممتاز")
    test_suite.record_test_result("test3", "S001", 18, "أداء جيد")
    
    test_suite.record_test_result("test1", "S002", 14, "أداء ممتاز")
    test_suite.record_test_result("test2", "S002", 9, "أداء جيد")
    test_suite.record_test_result("test3", "S002", 19, "أداء ممتاز")
    
    test_suite.record_test_result("test1", "S003", 13, "أداء جيد")
    test_suite.record_test_result("test2", "S003", 7, "أداء مقبول")
    test_suite.record_test_result("test3", "S003", 16, "أداء جيد")
    
    # إنشاء تقرير
    report = test_suite.generate_report()
    print("تقرير الأداء:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # تصدير التقرير
    test_suite.export_report("fitness_report.json")
    print("\nتم تصدير التقرير إلى fitness_report.json") 