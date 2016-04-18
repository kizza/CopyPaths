import sublime
import sublime_plugin
import os

def alert(msg):
	sublime.message_dialog(msg)

def get_folder_path():
	extract_variables = sublime.active_window().extract_variables()
	return extract_variables["folder"]

def get_file_path():
	extract_variables = sublime.active_window().extract_variables()
	file_path = extract_variables["file"]
	folder_path = extract_variables["folder"]
	file_path = file_path.replace(folder_path, "")
	return file_path[1:]

def get_test_path():
	file_path = get_file_path()
	if "_test.rb" in file_path:
		test_path = file_path
	else:
		test_path = file_path.replace("app/", "test/").replace(".rb", "_test.rb")
	if not os.path.exists(get_folder_path() + "/" + test_path):
		alert("Test file does not exist:\n"+test_path)
		return False
	return test_path

def execute_terminal(cmd):
	path = get_folder_path()
	cmd = cmd.replace('\"', '\\\"')
	print("running "+cmd + " in " + path)
	script = """osascript<<END
		tell application "Terminal"
		    activate
		    if not (exists window 1) then
		    	do script "cd %s; clear;"
		    else
		    	do script "cd %s; clear;" in window 1
		    end
		    repeat
	            delay 0.5
	            if not busy of window 1 then exit repeat
	        end repeat
	        do script "%s" in window 1
		end tell
END""" % (path, path, cmd)
	os.system(script)

class OpenTestFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		test_file = get_folder_path() + '/' + get_test_path()
		sublime.active_window().open_file(test_file, sublime.ENCODED_POSITION)

class CopyFilePathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(get_file_path())

class CopyTestPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sublime.set_clipboard(get_test_path())

class ExecuteTestPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		test_path = get_test_path()
		if test_path:
			cmd = "bin/rake test " + test_path
			execute_terminal(cmd)

class ExecuteIndividualTestPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = sublime.active_window().active_view()
		folder = get_folder_path()
		cursor = view.sel()
		if len(cursor) != 1:
			alert("Invalid selection")
			return

		lines = view.lines(sublime.Region(0, view.size()))
		last_valid = False
		test_match = ""
		for line in lines:
			if 'test "' in view.substr(line):
				last_valid = line
			if line.contains(cursor[0]) and last_valid:
				test_match = view.substr(last_valid)

		if test_match == "":
			alert("No individual test found")
			return

		test_name = test_match.replace('"', "").replace("do", "").strip().replace(" ", "_")
		cmd = "bin/rake test %s TESTOPTS=\"--name=%s\"" % \
			(get_test_path(), test_name)
		execute_terminal(cmd)
