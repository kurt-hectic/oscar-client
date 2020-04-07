# oscar-lib

A library to interact with OSCAR/Surface, developed by the WMO Community and kick-started by the WMO Secretariat. The oscar-lib allows to batch create stations using simple Python objects, and it also has support for downloading and changing information in OSCAR/Surface directly. Currently the modification of schedules is supported. More extensive documentation is currently being worked on.

For more details on how to use the library, see the [series of example code](https://github.com/kurt-hectic/wmo-notebooks) provided in jupyter notebooks.

This library is a community effort and supported by the WMO community, through the [OSCAR/Surface support forum](https://etrp.wmo.int/mod/forum/view.php?id=10062). Everybody is welcome to contribute to oscar-lib, please work through github to suggest improvements or post to the forum. As oscar-lib is a community-lead effort, the official OSCAR/Surface helpdesk at MeteoSwiss can not provide support for the oscar-lib.

Some part of the code, grouped in the object OscarGUIClient, is experimental and uses an internal API of OSCAR/Surface. These methods should be used with care and awareness that the internal API endpoint in OSCAR/Surface may change.
