rm -rif HackerMode
rm -rif ~/.HackerMode
rm $(which HackerMode)
git clone https://github.com/Arab-developers/HackerMode
echo -e "\n# start installing.../"
python3 -B HackerMode delete
python3 -B HackerMode install
rm HackerModeInstall