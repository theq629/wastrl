from PyInstaller.utils.hooks import collect_data_files

hiddenimports = [
	"cffi"
]

datas = collect_data_files('tcod')
datas += collect_data_files('tdl')
