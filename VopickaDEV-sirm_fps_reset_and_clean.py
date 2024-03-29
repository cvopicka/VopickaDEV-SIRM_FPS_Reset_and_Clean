#! /usr/bin/env python3

# region - Dependencies
try:
    errstat = False
    __dependencies__ = []

    trying = "logging"
    __dependencies__.append(trying)
    import logging

    trying = "sys"
    __dependencies__.append(trying)
    import sys

    assert sys.version_info >= (
        3,
        6,
    ), f"Incorrect Python version -- {sys.version_info} -- must be at least 3.6"

    trying = "pathlib"
    __dependencies__.append(trying)
    from pathlib import Path, PurePath

    trying = "datetime.datetime"
    __dependencies__.append(trying)
    from datetime import datetime

    # TODO - Add requirements

    trying = "pyodbc"
    __dependencies__.append(trying)
    import pyodbc

    trying = "toml"
    __dependencies__.append(trying)
    import toml

    trying = "pywebio"
    __dependencies__.append(trying)
    from pywebio import output, exceptions

    trying = "pywebio_battery"
    __dependencies__.append(trying)
    from pywebio_battery import confirm

    trying = "sirm_spf_libs"
    __dependencies__.append(trying)
    from sirm_spf_libs.Config import database_dsn

except ImportError:
    errstat = True
finally:
    # DOC - Configure the logging system

    # REM - Path tricks for making executable file
    if getattr(sys, "frozen", False):
        runfrom = sys.executable
    else:
        runfrom = __file__

    logging.basicConfig(
        filename=Path(
            PurePath(sys.argv[0]).parent / "Logs",
            f"{PurePath(sys.argv[0]).stem}-{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.log",
        ),
        format="%(asctime)s-[%(levelname)s]-(%(filename)s)-<%(funcName)s>-#%(lineno)d#-%(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        filemode="w",
        level=logging.WARNING,
    )

    # REM - Configure a named logger to NOT use the root log
    logger = logging.getLogger(sys.argv[0].replace(".py", ""))
    logger.setLevel(logging.DEBUG)

    # REM - Configure and add console logging to the named logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s-[%(levelname)s]-%(message)s"))
    logger.addHandler(console)

    if errstat is True:
        logger.fatal(f"Find missing library! -->{trying}<--")
        raise SystemExit(f"Find missing library! -->{trying}<--")

    # REM - Clean up
    del trying
    del errstat
# endregion - Dependencies

# region Header Block #########################################################
__project__ = runfrom
__purpose__ = "Reset a database deleteing generated data and clearing flags"
__license__ = "BSD3"
__maintainer__ = "Charles E. Vopicka"
__email__ = "chuck@vopicka.dev"

__status__ = "Prototype"
# __status__ = "Development"
# __status__ = "Production"

__revisionhistory__ = [
    ["Date", "Type", "Author", "Comment"],
    ["2024.01.21", "Created", __maintainer__, "Script Created"],
]
__created__ = __revisionhistory__[1][0]
__author__ = __revisionhistory__[1][2]
__version__ = __revisionhistory__[len(__revisionhistory__) - 1][0]
if __created__.split(".")[0] != __version__.split(".")[0]:
    __copyright__ = f'Copyright {__created__.split(".")[0]} - {__version__.split(".")[0]}, {__maintainer__}'
else:
    __copyright__ = f'Copyright {__created__.split(".")[0]}, {__maintainer__}'

__copyrightstr__ = "This program is licensed under the BSD 3 Clause license\n\n"
__copyrightstr__ += "See the LICENSE file for more information"

__credits__ = []
for n, x in enumerate(__revisionhistory__):
    if x[2] not in __credits__ and n > 0:
        __credits__.append(x[2])

appcredits = "\n".join(
    (
        __purpose__,
        f"\nBy:\t{__author__}",
        f"\t{__email__}",
        "",
        f"License:\t{__license__}",
        "",
        __copyright__,
        "",
        __copyrightstr__,
        f"\nCreated:\t{__created__}",
        f"Version:\t{__version__} ({__status__})",
        f"Rev:\t\t{len(__revisionhistory__) - 1}",
    )
)

logger.info(f"\n{appcredits}\n")

# endregion Header Block ######################################################


sqlstatements = toml.load(
    Path(
        PurePath(sys.argv[0]).parent,
        "SQL.toml",
    )
)

databasedsn = database_dsn()

if __name__ == "__main__":
    output.put_html("<h1>" + Path(sys.argv[0]).stem + "</h1>")

    output.put_code(appcredits)

    if confirm(
        "Confirm Database",
        databasedsn["DBQ"],
    ):
        output.put_info(f"File Selected: {databasedsn['DBQ']}")

        with pyodbc.connect(
            f"Driver={{{databasedsn['DRIVER']}}};"
            f"Dbq={PurePath(databasedsn['DBQ'])};"
            f"Uid={databasedsn['UID']};"
            f"Pwd=;"
        ) as dbconn:
            with dbconn.cursor() as dbcurs:
                for table, sql in dict(sqlstatements["tables"]).items():
                    if confirm(f"{table} action?", sql):
                        dbcurs.execute(sql)
                        logger.info(f"Ran: {sql} on {databasedsn['DBQ']}")
                        output.put_success(f"Ran: {sql} on {databasedsn['DBQ']}")

        output.put_success("Operation complete.")

    output.put_success("'Compact and Repair' your database now")
