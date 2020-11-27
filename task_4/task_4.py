import tools_from_task_1
import pymysql
import xml.etree.ElementTree as ET
from sys import exit
from typing import Dict, List, Tuple


class FourthTaskExportFilePreparationTool(tools_from_task_1.ExportPreparationTool):
    """
    Export preparation tool for exporting data to file
    """
    def get_prepared_data(self) -> Dict[str, List[dict]]:
        self.import_tool.import_data()
        return self.import_tool.stats


class FourthTaskExportMysqlPreparationTool(tools_from_task_1.FirstTaskJSONExportPreparationTool):
    """
    Export preparation tool for exporting initial data to Mysql database
    """
    def get_prepared_data(self) -> Tuple[list, list]:
        prepared_data = super().get_prepared_data()
        rooms = [(room['id'], room['name']) for room in prepared_data]
        students = []
        for room in prepared_data:
            for student in room['students']:
                student_info = (
                    student['id'],
                    student['name'],
                    student['sex'],
                    student['room'],
                    student['birthday']
                )
                students.append(student_info)
        return rooms, students


class FourthTaskJSONExportPreparationTool(FourthTaskExportFilePreparationTool):
    """
    Export preparation tool for exporting data to json file
    """
    pass


class FourthTaskXMLExportPreparationTool(FourthTaskExportFilePreparationTool):
    """
    Export preparation tool for exporting data to xml file
    """
    def get_prepared_data(self) -> ET.Element:
        prepared_data = super().get_prepared_data()
        root = ET.Element('stats')
        for stat_name, rooms in prepared_data.items():
            stat_element = ET.SubElement(root, stat_name)
            for room in rooms:
                room_element = ET.SubElement(stat_element, 'room')
                for key, value in room.items():
                    property_element = ET.SubElement(room_element, key)
                    property_element.text = str(value)
        return root


class FourthTaskExportMysqlTool(tools_from_task_1.ExportTool):
    """
    Exports data to Mysql database
    """
    def __init__(self, setup_tables: str, fill_tables: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_tables = setup_tables
        self.fill_tables = fill_tables

    def export_data(self) -> None:
        with self.output.cursor() as cursor:
            with open(self.setup_tables) as file:
                queries = map(lambda s: s.replace('\n', ''), file.read().split('\n\n'))
                for query in queries:
                    cursor.execute(query)

            rooms, students = self.export_preparation_tool.get_prepared_data()
            with open(self.fill_tables) as file:
                queries = map(lambda s: s.replace('\n', ''), file.read().split('\n\n'))
                for query, data in zip(queries, (rooms, students)):
                    # print(data)
                    cursor.executemany(query, data)

            self.output.commit()


class FourthTaskImportMysqlTool(tools_from_task_1.ImportTool):
    """
    Imports data from Mysql database
    """
    def __init__(self, fetch_db_data: str, connection: pymysql.Connection):
        self.connection = connection
        self.fetch_db_data = fetch_db_data
        self.stats = {}

    def import_data(self):
        with self.connection.cursor() as cursor, open(self.fetch_db_data) as file:
            queries = map(lambda s: s.replace('\n', ''), file.read().split('\n\n'))
            for num_of_query, query in enumerate(queries, start=1):
                cursor.execute(query)
                stat_name = f'stat_{str(num_of_query)}'
                self.stats[stat_name] = cursor.fetchall()


class FourthTask:
    AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS = {
        'json': (FourthTaskJSONExportPreparationTool, tools_from_task_1.FirstTaskJSONExportTool),
        'xml': (FourthTaskXMLExportPreparationTool, tools_from_task_1.FirstTaskXMLExportTool)
    }

    OUTPUT_FILE_NAME = 'rooms_and_students'

    try:
        #  Connection to database
        MYSQL_CONNECTION = pymysql.connect(
            host='localhost',
            user='task_4_user',
            password='task_4_password',
            db='task_4_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.err.OperationalError:
        exit('Connection to database failed! Change parameters for MYSQL_CONNECTION')

    #  Paths to files with SQL queries
    SETUP_TABLES_QUERIES = "setup_tables.txt"
    FILL_TABLES_QUERIES = "fill_tables.txt"
    FETCH_DB_QUERIES = "fetch_db_data.txt"

    @classmethod
    def execute_fourth_task(cls):
        """
        Start task execution
        """
        args = tools_from_task_1.CLI.get_args()

        import_files_tool = tools_from_task_1.FirstTaskImportTool(args.students, args.rooms)
        export_db_preparation_tool = FourthTaskExportMysqlPreparationTool(import_files_tool)
        export_db_tool = FourthTaskExportMysqlTool(cls.SETUP_TABLES_QUERIES, cls.FILL_TABLES_QUERIES,
                                                   cls.MYSQL_CONNECTION, export_db_preparation_tool)

        import_db_tool = FourthTaskImportMysqlTool(cls.FETCH_DB_QUERIES, cls.MYSQL_CONNECTION)
        export_preparation_tool_class, export_tool_class = cls.AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS[args.format]
        export_stats_tool = export_tool_class(cls.OUTPUT_FILE_NAME, export_preparation_tool_class(import_db_tool))

        try:
            export_db_tool.export_data()
            export_stats_tool.export_data()
        except (FileNotFoundError, PermissionError):
            print('Could not execute the task! Try to change input parameters.')


if __name__ == '__main__':
    FourthTask.execute_fourth_task()