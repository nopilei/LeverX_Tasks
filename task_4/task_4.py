import tools_from_task_1
import pymysql
import xml.etree.ElementTree as ET
from sys import exit
from typing import Dict, List, Tuple
from pprint import pprint


class FilePrepareDataTool(tools_from_task_1.ExportPreparationTool):
    """
    Export preparation tool for exporting data to file
    """
    def get_prepared_data(self) -> Dict[str, List[dict]]:
        self.import_tool.import_data()
        return self.import_tool.results


class MysqlPrepareDataTool(tools_from_task_1.JSONPreparationTool):
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


class JSONPrepareDataTool(FilePrepareDataTool):
    """
    Export preparation tool for exporting data to json file
    """
    pass


class XMLPrepareDataTool(FilePrepareDataTool):
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


class MysqlSetupTablesTool(tools_from_task_1.ExportTool):
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


class MysqlGetStatisticsTool(tools_from_task_1.ImportTool):
    """
    Executes queries defined in .sql files and collects results to .results attribute
    """
    def __init__(self, path_to_sql_queries: str, connection: pymysql.Connection):
        self.connection = connection
        self.path_to_sql_queries = path_to_sql_queries
        self.results = {}

    def import_data(self):
        with self.connection.cursor() as cursor, open(self.path_to_sql_queries) as file:
            queries = map(lambda s: s.replace('\n', ''), file.read().split('\n\n'))
            for num_of_query, query in enumerate(queries, start=1):
                cursor.execute(query)
                self.results[query] = cursor.fetchall()


class FourthTask:
    AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS = {
        'json': (JSONPrepareDataTool, tools_from_task_1.JSONExportTool),
        'xml': (XMLPrepareDataTool, tools_from_task_1.XMLExportTool)
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
    FETCH_DB_QUERIES = "path_to_sql_queries.sql"

    @classmethod
    def execute_fourth_task(cls):
        """
        Start task execution
        """
        args = tools_from_task_1.CLI.get_args()

        #  Setting up database
        import_initial_data_tool = tools_from_task_1.StudentsRoomsImportTool(args.students, args.rooms)
        setup_db_preparation_tool = MysqlPrepareDataTool(import_initial_data_tool)
        setup_db_tool = MysqlSetupTablesTool(cls.SETUP_TABLES_QUERIES, cls.FILL_TABLES_QUERIES,
                                             cls.MYSQL_CONNECTION, setup_db_preparation_tool)

        #  Exporting statistics to either json or xml file
        fetch_stats_from_db_tool = MysqlGetStatisticsTool(cls.FETCH_DB_QUERIES, cls.MYSQL_CONNECTION)
        export_preparation_tool_class, export_tool_class = cls.AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS[args.format]
        export_stats_to_file_tool = export_tool_class(cls.OUTPUT_FILE_NAME,
                                                      export_preparation_tool_class(fetch_stats_from_db_tool))

        try:
            setup_db_tool.export_data()
            export_stats_to_file_tool.export_data()
        except (FileNotFoundError, PermissionError):
            print('Could not export to file! Try to change input parameters.')


if __name__ == '__main__':
    FourthTask.execute_fourth_task()
