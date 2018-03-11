set -e

rm -rf temp dist
mkdir -p temp

virtualenv temp/venv
source temp/venv/bin/activate
pip install -r requirements.txt
pip install ..

version="$(pip show wastrl | grep '^Version:' | sed -e 's|^[A-Za-z]\+: *||g')"
echo "packaging version $version"

sed -e "s|{version}|$version|g" "readme.txt" > "temp/README"

pyinstaller \
	--name "wastrl-$version" \
	--noconfirm \
	--additional-hooks-dir=. \
	--add-data '../wastrl/config:wastrl/config' \
	--add-data '../wastrl/resources:wastrl/resources' \
	--add-data 'temp/README:.' \
	start-wastrl.py

rm -f "wastrl-$version.tar.gz"
{
	cd "dist"
	tar -zcvf "../wastrl-$version.tar.gz" "wastrl-$version"
}
