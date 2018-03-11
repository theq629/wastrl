import sys

readme_path = sys.argv[1]
version = sys.argv[2]
gameplay_path = sys.argv[3]

def demarkdown(text):
	return text.replace("`", "")

with open(readme_path) as readme_file:
	with open(gameplay_path) as gameplay_file:
		readme = readme_file.read().format(
			version = version,
			gameplay = demarkdown(gameplay_file.read())
		)
		sys.stdout.write(readme)
