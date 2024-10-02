# FFX Sphere Grid viewer
Program used to parse, display and edit (and in the future, export) a FFX Sphere Grid Layout.

Open `ffx_sphere_grid_viewer.py` to use.

# Custom Layout
You can construct a custom Layout and pass it to the `main` function to load that as a "Custom Layout" in the UI.

# Game Files
The program will attempt to find `dat[01/02/03/09/10/11].dat` and `panel.bin` in the `ffx_sphere_grid_viewer/data/data_files` folder, if they are not present the `.csv` files will be used instead. You can retrieve these `.dat` and `.bin` files from `ffx.exe` by extracting it's contents with a program such as `vbfextract`.

# Credits
Credits to the #modding channel in the [FFX/X-2 Speedruns Discord](https://discord.gg/X3qXHWG) for ideas and useful discussions.

Credits to [Karifean](https://github.com/Karifean) for his work on the [FFX Data Parser](https://github.com/Karifean/FFXDataParser), used as the basis for the file-parsing functions.
