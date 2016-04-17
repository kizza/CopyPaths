import sublime
import sublime_plugin
import os

def get_folder_path():
	extract_variables = sublime.active_window().extract_variables()
	return extract_variables["folder"]

def get_file_path():
	extract_variables = sublime.active_window().extract_variables()
	file_path = extract_variables["file"]
	folder_path = extract_variables["folder"]
	return file_path.replace(folder_path, "")

def get_test_path():
	file_path = get_file_path()
	if "_test.rb" in file_path:
		test_path = file_path
	else:
		test_path = file_path.replace("app/", "test/").replace(".rb", "_test.rb")
	if not os.path.exists(get_folder_path() + test_path):
		sublime.message_dialog("Test file does not exist:\n"+test_path)
	return test_path[1:]

class CopyFilePathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(get_file_path())

class CopyTestPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(get_test_path())

class CopyRakeTestPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		test_path = get_test_path()
		sublime.set_clipboard("bin/rake test " + test_path)
