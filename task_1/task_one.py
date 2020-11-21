import json
import xml.etree.ElementTree as ET
import argparse
from typing import Any, List


class ExportPreparationTool:
    """
    Before exporting any data, you have to get initial data and then process it if needed.
    This class defines interface for such tools
    """
    def import_data(self) -> None:
        """
        Import data from any source or sources
        """
        raise NotImplementedError

    def prepare_data(self) -> Any:
        """
        Implements data processing logic (which is defined by particular task requirements) for future exporting
        """
        raise NotImplementedError

    def import_and_prepare(self) -> Any:
        self.import_data()
        return self.prepare_data()


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


class TaskExportPreparationTool(ExportPreparationTool):
    """
    Export preparation tool for this task
    """
    def __init__(self, students_path: str, rooms_path: str):
        self.students_path = students_path
        self.rooms_path = rooms_path
        self.students, self.rooms = [], []

    def import_data(self) -> None:
        """
        Loads students.json and rooms.json files
        """
        with open(self.students_path) as s_file, open(self.rooms_path) as r_file:
            self.students = json.load(s_file)
            self.rooms = json.load(r_file)

    def prepare_data(self) -> List[dict]:
        """
        Data processing logic
        """
        output_data = {}
        for room in self.rooms:
            output_data[room['id']] = room.copy()
            output_data[room['id']]['students'] = []

        for student in self.students:
            output_data[student['room']]['students'].append(student.copy())

        return list(output_data.values())


class TaskJSONExportTool(ExportTool):
    """
    Exports data to json file
    """
    def export_data(self) -> None:
        prepared_data = self.export_preparation_tool.import_and_prepare()
        with open(f'{self.output}.json', 'w') as file:
            json.dump(prepared_data, file)


class TaskXMLExportTool(ExportTool):
    """
    Exports data to xml file
    """
    def export_data(self) -> None:
        """
        Since the prepared data format is not compatible with xml files, we need to make some steps to reformat it
        """
        prepared_data = self.export_preparation_tool.import_and_prepare()
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

        ET.ElementTree(root).write(f'{self.output}.xml')


class Task:
    """
    Task execution
    """
    AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS = {
        'json': TaskJSONExportTool,
        'xml': TaskXMLExportTool
    }
    AVAILABLE_EXTENSIONS = list(AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS.keys())

    def __init__(self, export: ExportTool):
        self.export = export

    @classmethod
    def solve_task(cls):
        """
        Start task execution
        """
        try:
            parser = argparse.ArgumentParser(
                description='Given paths to input json files, fetches data from these files, '
                'processes it and outputs new info in either xml or json file')
            parser.add_argument('rooms', help='Path to rooms.json')
            parser.add_argument('students', help='Path to students.json')
            parser.add_argument('--format',
                                help='Format of output file (extension). Defaults to json',
                                choices=cls.AVAILABLE_EXTENSIONS, default='json')
            parser.add_argument('--output',
                                help='Full name of output file without extension. Defaults to "rooms_and_students"',
                                default='rooms_and_students')
            args = parser.parse_args()

            export_tool_class = cls.AVAILABLE_EXTENSIONS_AND_EXPORT_TOOLS[args.format]
            export_tool = export_tool_class(args.output, TaskExportPreparationTool(args.students, args.rooms))
            export_tool.export_data()

        except (FileNotFoundError, PermissionError):
            print('Could not execute the task! Try to change input arguments.')


if __name__ == '__main__':
    Task.solve_task()


