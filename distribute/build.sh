set -e

version="$1"

if [ ! "$version" ]; then
	echo "error: need to give version" 1>&2
	exit 1
fi

rm -rf temp
mkdir -p temp
sed -e "s|{version}|$version|g" "readme.txt" > "temp/README"

rm -rf "dist"
pyinstaller \
	--name "wastrl-$version" \
	--noconfirm \
	--additional-hooks-dir=. \
	--add-data '../wastrl/config:wastrl/config' \
	--add-data '../wastrl/resources:wastrl/resources' \
	--add-data 'temp/README:.' \
	start-wastrl.py

rm -f "wastrl-$version.zip"
{
	cd "dist"
	zip -r "../wastrl-$version.zip" "wastrl-$version"
}
