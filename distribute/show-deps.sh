pip list --format columns | awk 'NR > 2 { print }' | while read p v; do pip show $p | grep '^License\|^Home-page' | sed -e 's|^[A-Za-z-]\+: *||g' | tr '\n' ' ' | sed -e 's| *$||g'; echo; done
