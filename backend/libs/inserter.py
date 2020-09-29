def databaseInsert(host, user, passwd, db, csv_file):
    import csv
    import MySQLdb
    import os
    mydb = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cursor = mydb.cursor()
    csv_data = csv.reader(open(csv_file))
    for row in csv_data:
        print("Running Insert: {0}".format(row))
        cursor.execute('INSERT INTO objects(object_type,object_diraction, object_speed,object_capture_date )'
                       'VALUES(%s, %s, %s,%s)',
                       row)
    # close the connection to the database.
    mydb.commit()
    cursor.close()
    os.system("rm -rf %s;touch %s" % (csv_file, csv_file))
    print("Insert Into database finished")


def historyDatabaseInsert(host, user, passwd, db, action):
    import csv
    import MySQLdb
    import os
    mydb = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    cursor = mydb.cursor()
    csv_data = csv.reader(open(csv_file))
    for row in csv_data:
        print("Running Insert: {0}".format(row))
        cursor.execute('INSERT INTO objects(object_type,object_diraction, object_speed,object_capture_date )'
                       'VALUES(%s, %s, %s,%s)',
                       row)
    # close the connection to the database.
    mydb.commit()
    cursor.close()
    os.system("rm -rf %s;touch %s" % (csv_file, csv_file))
    print("Insert Into database finished")
