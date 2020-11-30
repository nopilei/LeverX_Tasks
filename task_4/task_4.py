import IOtools
import pymysql
import xml.etree.ElementTree as ET
from sys import exit
from typing import Dict, List, Tuple
from pprint import pprint


class FilePreparationTool(IOtools.ExportPreparationTool):
    """
    Export preparation tool for exporting data to file
    """
    def get_prepared_data(self) -> Dict[str, List[dict]]:
        self.import_tool.import_data()
        return self.import_tool.imported_data


class MysqlPreparationTool(IOtools.JSONPreparationTool):
    """
    Export preparation tool for filling Mysql database
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


class JSONPreparationTool(FilePreparationTool):
    """
    Export preparation tool for exporting data to json file
    """
    pass


class XMLPreparationTool(FilePreparationTool):
    """
    Export preparation tool for exporting data to xml file
    """
    def get_prepared_data(self) -> ET.Element:
        prepared_data = super().get_prepared_data()
        root = ET.Element('results')
        for stat_name, rooms in prepared_data.items():
            stat_element = ET.SubElement(root, stat_name)
            for room in rooms:
                room_element = ET.SubElement(stat_element, 'room')
                for key, value in room.items():
                    property_element = ET.SubElement(room_element, key)
                    property_element.text = str(value)
        return root


class MysqlSetupTablesTool(IOtools.ExportTool):
    """
    Sets up Mysql database
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
                    cursor.executemany(query, data)

            self.output.commit()


class MysqlGetStatsTool(IOtools.ImportTool):
    """
    Executes queries defined in statistics.sql file
    """
    def __init__(self, path_to_sql_queries: str, connection: pymysql.Connection):
        super().__init__()
        self.connection = connection
        self.path_to_sql_queries = path_to_sql_queries

    def import_data(self):
        with open(self.path_to_sql_queries) as file:
            queries_and_names = map(lambda s: s.replace('\n', ''), file.read().split('\n\n'))
        with self.connection.cursor() as cursor:
            for query_and_name in queries_and_names:
                query_name = query_and_name[1:query_and_name.rfind('#')]
                query = query_and_name[query_and_name.rfind('#') + 1:]
                cursor.execute(query)
                self.imported_data[query_name] = cursor.fetchall()


class FourthTask:
    AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS = {
        'json': (JSONPreparationTool, IOtools.JSONExportTool),
        'xml': (XMLPreparationTool, IOtools.XMLExportTool)
    }

    OUTPUT_FILE_NAME = 'rooms_and_students'

    try:
        #  Connect to Mysql database
        MYSQL_CONNECTION = pymysql.connect(
            host='localhost',
            user='task_4_user',
            password='task_4_password',
            db='task_4_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.err.OperationalError:
        exit('Connection to database failed! Set proper parameters for MYSQL_CONNECTION')

    #  Paths to files with SQL queries
    SETUP_TABLES_QUERIES = "setup_tables.sql"
    FILL_TABLES_QUERIES = "fill_tables.sql"
    STATS_QUERIES = "statistics.sql"

    @classmethod
    def execute_fourth_task(cls):
        """
        Start task execution
        """
        args = IOtools.CLI.get_args()

        #  Setting up database
        import_initial_data_tool = IOtools.StudentsRoomsImportTool(args.students, args.rooms)
        setup_db_preparation_tool = MysqlPreparationTool(import_initial_data_tool)
        setup_db_tool = MysqlSetupTablesTool(cls.SETUP_TABLES_QUERIES, cls.FILL_TABLES_QUERIES,
                                             cls.MYSQL_CONNECTION, setup_db_preparation_tool)

        #  Exporting statistics to either json or xml file
        fetch_stats_from_db_tool = MysqlGetStatsTool(cls.STATS_QUERIES, cls.MYSQL_CONNECTION)
        export_preparation_tool_class, export_tool_class = cls.AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS[args.format]
        export_stats_to_file_tool = export_tool_class(cls.OUTPUT_FILE_NAME,
                                                      export_preparation_tool_class(fetch_stats_from_db_tool))

        try:
            setup_db_tool.export_data()
            export_stats_to_file_tool.export_data()
        except (FileNotFoundError, PermissionError):
            print('Could not export to file! Try to change input parameters.')

        #  Take a look at 'statistics.sql'. There are all SQL queries, required by task, and their names,
        #  separated by '#'.

        #  To see all names of queries, use
        pprint(list(fetch_stats_from_db_tool.imported_data.keys()))
        print()
        #  To see result of a particular query, use
        query_name = 'top 5 комнат, где самые маленький средний возраст студентов'
        pprint(fetch_stats_from_db_tool.imported_data[query_name])


if __name__ == '__main__':
    FourthTask.execute_fourth_task()
