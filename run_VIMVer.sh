
<<'###BLOCK-COMMENT'
echo "Check for dependencies..."

FILE="$(pwd)/settings" 

if [ -f "$FILE" ]; then

    while IFS= read -r line; do
        if [ grep "dependencies=1" $line ]; then
            echo "...dependencies ok"
            fi
        done < "$FILE"

else

    touch $FILE

    for module in 'django' 'Bio' 'logomaker' ; do 
        python -c "import ${module}"
        if [ $? ]; then
            python3 -m pip install ${module}
            fi
        done
    
    "dependencies=1" > $FILE
    fi

echo "...dependencies ok"

###BLOCK-COMMENT


firefox http://10.1.2.200/ &

ViralOceanView/manage.py runserver 10.1.2.200




