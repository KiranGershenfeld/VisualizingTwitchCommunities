from calc_overlaps import OverlapsManager
import sqlalchemy as sql
from sqlalchemy.sql.expression import func
import os
from dotenv import load_dotenv
import datetime
from py4j.java_gateway import JavaGateway



RECALC_OVERLAPS = True
POST_IMAGE_TO_TWITTER = False

def main():

    if RECALC_OVERLAPS:
        start_time = datetime.date.today()
        end_time = start_time - datetime.timedelta(days=30)

        OM = OverlapsManager(start_time=start_time, end_time=end_time, db_url=os.environ.get("DB_URL"))
        OM.run()
        OM.dump_overlaps_to_db()

    gateway = JavaGateway()                        # connect to the JVM
    java_object = gateway.jvm.mypackage.MyClass()  # invoke constructor
    other_object = java_object.doThat()
    other_object.doThis(1,'abc')
    gateway.jvm.java.lang.System.out.println('Hello World!') # call a static metho

    if POST_IMAGE_TO_TWITTER:
        pass

    return


if __name__ == "__main__":
    load_dotenv()
    main()