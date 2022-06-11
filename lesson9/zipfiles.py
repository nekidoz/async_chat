from dataclasses import dataclass
import datetime
import argparse
import re
import os
import subprocess


@dataclass
class CamData:
    name: str                           # camera name
    fileSearchPattern: str              # e.g. 'P*.jpg'
    fileSetSearchPattern: str           # e.g. 'P202107*.jpg'
    fileDateSubstringPos: tuple         # e.g. (2, 5) - from the 2 to the 5 symbol
    fileDateFormat: str                 # e.g. '%Y%m%d'
    archiveFileSetPattern: str          # e.g. 'P202107*.jpg'
    archiveNamePattern: str             # e.g. 'P2107.zip'
    archiveDateFormat: str              # e.g. '%y%m'


CAMERAS = [
    CamData(name="CAM1",
            fileSearchPattern=r"C1-.*\.jpg",
            fileSetSearchPattern=r"P{}.*\.jpg",
            fileDateSubstringPos=(1, 9),
            fileDateFormat="%Y%m%d",
            archiveFileSetPattern="P{}*.jpg",
            archiveNamePattern="P{}.zip",
            archiveDateFormat="%y%m"),
    CamData(name="CAM2",
            fileSearchPattern=r"C2-.*\.jpg",
            fileSetSearchPattern=r"F{}.*\.jpg",
            fileDateSubstringPos=(1, 8),
            fileDateFormat="%Y%m%d",
            archiveFileSetPattern="F{}*.jpg",
            archiveNamePattern="F{}.zip",
            archiveDateFormat="%y%m"),
]
DEFAULT_PATH = "."
TEST_PATH = "testUnarchive"
ARCHIVE_COMMAND = "zip -q"
UNARCHIVE_COMMAND = "unzip -uoq -d " + TEST_PATH
COMPARE_COMMAND = "diff -q"
REMOVE_COMMAND = "rm"
REMOVE_DIR_COMMAND = "rmdir"


class OSCommand:
    def __init__(self):
        self.command = None
        self.path = None
        self.title = None
        self.exit_code = 0
        self.error_message = None
        pass

    def execute(self, command: str, path: str = None, title: str = None):
        """ Raises exception if fails """
        path = path if path else "."
        self.command = command
        self.path = path
        self.title = title
        if title:
            print(title)
        # print(f"Command: {command}")
        # print(f"Path: {path}")
        with subprocess.Popen(command, cwd=path, shell=True, stderr=subprocess.PIPE) as process:
            self.exit_code = process.wait()
            # print(f"Exit code: {exitCode}")
            if self.exit_code:
                self.error_message = process.stderr.read().decode().strip()
                raise Exception
            else:
                self.error_message = None


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', required=False)
    args = parser.parse_args()
    # Init arguments
    path = args.path if args.path else DEFAULT_PATH
    print(f"Searching path: {path}")

    os_command = OSCommand()
    error = False
    warning = False
    report_list = []

    for camera in CAMERAS:
        print()
        print(f"Searching for camera {camera.name} files...")
        any_files = False
        while True:
            error = True
            print()
            # Find the first file to search for the whole portion afterwards
            try:
                with os.scandir(path) as files_list:
                    try:
                        file_name = next(f.name for f in files_list
                                         if f.is_file() and re.match(camera.fileSearchPattern, f.name))
                        any_files = True
                    except StopIteration:
                        if not any_files:
                            report_list.append(f"WARNING: No camera {camera.name} files found.")
                            print(report_list[-1:][0])
                            warning = True
                        error = False
                        break
            except FileNotFoundError as e:
                report_list.append(f"Error searching files of camera {camera.name}: {e}")
                print(report_list[-1:][0])
                break
            # Extract date period from file name to compose a set
            # print(f"File name found: {file_name}")
            date_part = file_name[camera.fileDateSubstringPos[0]:camera.fileDateSubstringPos[1]]
            date_value = datetime.datetime.strptime(date_part, camera.fileDateFormat).date()
            # print(f"File name date part: {date_part}, date: {date_value}")
            # Find the whole file set to be zipped
            file_pattern = camera.fileSetSearchPattern.format(date_part)
            print(f"Looking for files: {file_pattern} dated {date_value}")
            try:
                with os.scandir(path) as files_list:
                    file_set = [f.name for f in files_list if f.is_file() and re.match(file_pattern, f.name)]
            except FileNotFoundError as e:
                report_list.append(f"ERROR: searching files {file_pattern} of camera {camera.name}: {e}")
                print(report_list[-1:][0])
                break
            # print(file_set)
            # print(f"{len(file_set)} files found.")
            try:
                # Zip the files
                archive_date_part = date_value.strftime(camera.archiveDateFormat)
                archive_file_name = camera.archiveNamePattern.format(archive_date_part)
                command = " ".join((ARCHIVE_COMMAND, archive_file_name, *file_set))
                os_command.execute(command, path, "Archiving files...")
                # Unzip files to test location
                command = " ".join((UNARCHIVE_COMMAND, archive_file_name, *file_set))
                os_command.execute(command, path, "Unarchiving files for comparison...")
                # Compare source and test files
                print("Comparing files...")
                for fileName in file_set:
                    command = " ".join((COMPARE_COMMAND, fileName, "/".join((TEST_PATH, fileName))))
                    os_command.execute(command, path)
                # Remove files
                command = " ".join((REMOVE_COMMAND, *file_set))
                test_path = "/".join((path, TEST_PATH))
                os_command.execute(command, test_path, "Removing test files...")
                os_command.execute(command, path, "Removing source files...")
                command = " ".join((REMOVE_DIR_COMMAND, TEST_PATH))
                os_command.execute(command, path, "Removing test directory...")
            except Exception:
                report_list.append(f"ERROR ({os_command.exit_code}): adding {camera.name} camera {len(file_set)} files "
                                   f"{file_pattern} dated {date_value} to archive {archive_file_name}, "
                                   f"stage {os_command.title}: {os_command.error_message}.")
                print(report_list[-1:][0])
                break
            report_list.append(f"SUCCESS: {camera.name} camera {len(file_set)} files {file_pattern} "
                               f"dated {date_value} added to archive {archive_file_name}.")
            print(report_list[-1:][0])
            #error = False
            #break

        if error:
            break


if __name__ == "__main__":
    main()
