# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import sys
# print(sys.executable)
import mysql.connector
from mysql.connector import errorcode


class DtekParserPipeline:
    """Gets items from DTEK site and stores them in database"""

    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        """Basic database connection setup"""

        self.connection = mysql.connector.connect(
            host='localhost',
            user='serviceuser',
            passwd='Strong_p@ssword',
            database='info_bot'
        )
        self.cursor = self.connection.cursor()
        print('Connected to the database.')

    def create_table(self):
        """Creating table if it is not there. Otherwise, output a message and continue"""

        items_table = (
            "CREATE TABLE `info_bot`.`outages` ("
            "`id` int NOT NULL AUTO_INCREMENT,"
            "`outage_date` VARCHAR(45) NULL,"
            "`turn_on_date` VARCHAR(45) NULL,"
            "`area` VARCHAR(45) NULL,"
            "`all_towns_and_streets` LONGTEXT NULL DEFAULT NULL,"
            "`works_type` VARCHAR(45) NULL,"
            "`posting_date` VARCHAR(45) NULL,"
            "`outage_schedule` VARCHAR(45) NULL,"
            "`status` VARCHAR(45) NULL,"
            "PRIMARY KEY (`index`));"
        )
            # "CREATE TABLE `employees` ("
            # "  `emp_no` int(11) NOT NULL AUTO_INCREMENT,"
            # "  `birth_date` date NOT NULL,"
            # "  `first_name` varchar(14) NOT NULL,"
            # "  `last_name` varchar(16) NOT NULL,"
            # "  `gender` enum('M','F') NOT NULL,"
            # "  `hire_date` date NOT NULL,"
            # "  PRIMARY KEY (`emp_no`)"
            # ") ENGINE=InnoDB")
        try:
            self.cursor.execute(items_table)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table already exists.")
            else:
                print(err.msg)
        else:
            print("Table created")

    def store_item(self, item):
        """Store passed item to database"""

        self.cursor.execute("INSERT INTO outages "
                            "(outage_date, turn_on_date, area, all_towns_and_streets, works_type, "
                            "posting_date, outage_schedule, status ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (item.outage_date,
                             item.turn_on_date,
                             item.area,
                             item.all_towns_and_streets,
                             item.works_type,
                             item.posting_date,
                             item.outage_schedule,
                             item.status,
                             )
                            )
        self.connection.commit()
        print("Item inserted")

    def process_item(self, item):
        # todo get item- data-id
        # if item['data-id']
        self.store_item(item)
        print(item.works_type)
        # print('########1')
        # todo set up archive table and transfer items there after their action time is expired
        return item
