# FILTRO

This project takes specific tab seperated txt files generated by a server, and converts them all into xlsx format. 

The data is of the format present here(just example data real data may vary but should be of similar format):                               
[sample data.txt](https://github.com/user-attachments/files/16194871/sample.data.txt)



Then that data is summarized on the following basis: 
1) Is the IP present in all files (ideal cases), if not then in how many.
2) How many times response error has been occurred? Here fld3 & fld4 is empty.
3) How many times connection error has occurred? Here PRIMKEY is empty.

And this summary file is generated as an excel sheet at the press of a button.

![image](https://github.com/user-attachments/assets/c623286b-1bb0-4c06-9439-a2c7e7bf7273)
The web app

![image](https://github.com/user-attachments/assets/ce7d0e03-a621-41ff-8345-6df43a84aa20)
All the txt files converted into xlsx files

![image](https://github.com/user-attachments/assets/9c4bd4b7-9adb-4e46-add0-7e1ec2abf789)

Summary generated
