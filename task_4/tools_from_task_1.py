import json
import xml.etree.ElementTree as ET
import argparse
from typing import Any, List

# =====================================
# INTERFACES
# =====================================


class ImportTool:
    """
    Interface for tools that import data
    """
    def import_data(self) -> Any:
        """
        Import data from any source or sources
        """
        raise NotImplementedError


class ExportPreparationTool:
    """
    Before exporting any data, you have to probably transform it.
    This class defines interface for such tools
    """
    def __init__(self, import_tool: ImportTool):
        """
        Set import tool as an instance attribute (as you need to first import data before preparation)
        """
        self.import_tool = import_tool

    def get_prepared_data(self) -> Any:
        """
        Implements data processing logic (which is defined by particular task requirements) for future exporting
        """
        raise NotImplementedError


class ExportTool:
    """
    Interface for exporting data to particular source(file, database, etc.)
    Output argument represents the destination source(filename, database connection, etc.)
    """
    def __init__(self, output: Any, export_preparation_tool: ExportPreparationTool):
        self.output = output
        self.export_preparation_tool = export_preparation_tool

    def export_data(self) -> None:
        """
        Export data to any source or sources
        """
        raise NotImplementedError


# =====================================
# IMPLEMENTATIONS
# =====================================


class FirstTaskImportTool(ImportTool):
    """
    Import tool for the first task
    """
    def __init__(self, students_path: str, rooms_path: str):
        self.students_path = students_path
        self.rooms_path = rooms_path
        self.students, self.rooms = [], []

    def import_data(self) -> None:
        """
        Loads 'student.json' and 'rooms.json'
        """
        with open(self.students_path) as s_file, open(self.rooms_path) as r_file:
            self.students = json.load(s_file)
            self.rooms = json.load(r_file)


class FirstTaskExportPreparationTool(ExportPreparationTool):
    """
    Export preparation tool for the first task
    """
    def get_prepared_data(self) -> List[dict]:
        """
        Data processing logic
        """
        self.import_tool.import_data()
        output_data = {}
        for room in self.import_tool.rooms:
            output_data[room['id']] = room.copy()
            output_data[room['id']]['students'] = []

        for student in self.import_tool.students:
            output_data[student['room']]['students'].append(student.copy())

        return list(output_data.values())


class FirstTaskJSONExportPreparationTool(FirstTaskExportPreparationTool):
    """
    Export json preparation tool for the first task
    """
    pass


class FirstTaskXMLExportPreparationTool(FirstTaskExportPreparationTool):
    """
    Export xml preparation tool for the first task
    """
    def get_prepared_data(self) -> ET.Element:
        """
        Since the prepared data format is not compatible with xml files, we need to make some steps to reformat it
        """
        prepared_data = super().get_prepared_data()
        root = ET.Element('rooms')
        for room in prepared_data:
            room_element = ET.SubElement(root, 'room')

            room_students = room.pop('students')
            room_students_element = ET.SubElement(room_element, 'students')

            for key, value in room.items():
                room_property = ET.SubElement(room_element, key)
                room_property.text = str(value)

            for student in room_students:
                room_student_element = ET.SubElement(room_students_element, 'student')
                for key, value in student.items():
                    student_property = ET.SubElement(room_student_element, key)
                    student_property.text = str(value)
        return root


class FirstTaskJSONExportTool(ExportTool):
    """
    Exports data to json file
    """
    def export_data(self) -> None:
        prepared_data = self.export_preparation_tool.get_prepared_data()
        with open(f'{self.output}.json', 'w') as file:
            json.dump(prepared_data, file)


class FirstTaskXMLExportTool(ExportTool):
    """
    Exports data to xml file
    """
    def export_data(self) -> None:
        root = self.export_preparation_tool.get_prepared_data()
        ET.ElementTree(root).write(f'{self.output}.xml')

# =====================================
# First task execution
# =====================================


class CLI:
    """
    CLI util for working with 'rooms', 'students' and 'format' parameters
    """
    AVAILABLE_EXTENSIONS = ['json', 'xml']

    @classmethod
    def get_args(cls) -> argparse.Namespace:
        """
        Get CLI arguments
        """
        parser = argparse.ArgumentParser(
            description='Given paths to input json files, fetches data from these files, '
                        'processes it and outputs new info in either xml or json file')
        parser.add_argument('rooms', help='Path to rooms.json')
        parser.add_argument('students', help='Path to students.json')
        parser.add_argument('--format',
                            help='Format of output file (extension). Defaults to json',
                            choices=cls.AVAILABLE_EXTENSIONS, default='json')
        args = parser.parse_args()
        return args


class FirstTask:
    """
    First task execution
    """
    AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS = {
        'json': (FirstTaskJSONExportTool, FirstTaskJSONExportPreparationTool),
        'xml': (FirstTaskXMLExportTool, FirstTaskXMLExportPreparationTool)
    }
    OUTPUT_FILE_NAME = 'rooms_and_students'

    @classmethod
    def execute_first_task(cls):
        """
        Start task execution
        """
        args = CLI.get_args()
        import_tool = FirstTaskImportTool(args.students, args.rooms)
        export_tool_class, export_preparation_tool_class = cls.AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS[args.format]
        export_tool = export_tool_class(cls.OUTPUT_FILE_NAME, export_preparation_tool_class(import_tool))
        try:
            export_tool.export_data()
        except (FileNotFoundError, PermissionError):
            print('Could not execute the task! Try to change input parameters.')


if __name__ == '__main__':
    FirstTask.execute_first_task()


