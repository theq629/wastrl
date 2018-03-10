pyinstaller \
	--noconfirm \
	--additional-hooks-dir=. \
	--add-data '../wastrl/config:wastrl/config' \
	--add-data '../wastrl/resources:wastrl/resources' \
	launch.py
