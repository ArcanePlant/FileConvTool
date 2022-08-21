import os

from modhelpers.mio import Mio
from modhelpers.math_util import MathUtils

"""
Notes

File formats

the game uses havok as a base, searching for "hkx" in the exe reveals much information about the used formats
chances are high that they used many default fields for the file format


GAMEDATA
    ARCHIVE
        pack        ...     Identifier: ALBS ==> SBLA
                            Streamblock archive?
                            May contain other identifier: 00ED
        dynpack     ...     Seems to be the same as a .pack
        pck         ...     Identifier: 1KCP
        megapack    ...     Identifier: 00PM
                            Contains ALBS in some kind of directory structure
        kilopack    ...     Renamed megapack
    ANIMATION
        cxa         ...     Animation data?
        fxa         ...     Data for FaceFX: https://facefx.com/documentation/2013/W37
        pak         ...     Part of FaceFX?
    TEXT
        dlg         ...     DiaLoG, binary, translations for the subtitles, maybe more
        rnd         ...     Random text? found in \Cinematics\Dialog\Random, different structure?
    MISC
        txt         ...     Littered about as different configuration files
        profile     ...     Save data structure?
    UNKNOWN
        cnvpack     ...
        cinpack     ...
        wsd         ...		starts with 00 00 00 00 0C 00 00 00
        vcr         ...     In directory 'recordings'
    FRANCE
        ambush      ...
        cinsplines  ...
        defen       ...
        freeplay    ...
        GpsGraph    ...
        hei         ...		5IEH (next field is number of 1IEH blocks in the file)
        hqpoints    ...
        materials   ...
        paths       ...
        railway     ...
        rndnodes    ...
        spore       ...
        trigs       ...
        waterctrl   ...
        waterflow   ...
        info        ...
        map         ...     6PAM ==> MAP6, part of DLC

GENERIC
    CONF
        ini         ...     Basic setup
    TEXTURES
        dds         ...     Direct Draw Surface
    VIDEO
        bik         ...     Bink Video
    SCRIPTING
        luap        ...     Compiled lua scripts
    FONTS
        ttf         ...     Normal ttf file
        otf         ...     Normal otf file
UNIQUE
    WWiseIDTable.bin


Unordered notes:
https://en.wikipedia.org/wiki/DotXSI is mentioned in a path in /Animations.pack
"""


def export_hei_as_ply(dir: str, filename: str):
    # x/y/z are denoted in Blenders coordinate system
    # DirectX: x/y/z
    # DirectX to Blender: x * -1/z/y
    file_path = os.path.join(dir, filename)
    with open(file_path, 'rb') as f:
        if Mio.read_fixed_length_string(4, 'ASCII', f) != '5IEH':
            raise ValueError('Invalid file')
        block_count = Mio.read_uint32le(f)
        maybe_x_max_block_count = Mio.read_uint32le(f)  # TODO check if (max x of all blocks / 60) is close to this value
        maybe_y_max_block_count = Mio.read_uint32le(f)  # TODO check if (max y of all blocks / 60) is close to this value
        global_sidelength = Mio.read_float32le(f)
        global_xmin = Mio.read_float32le(f)
        if Mio.read_uint32le(f) != 0:  # skipped, always 0
            raise ValueError('not 0')
        global_ymin = Mio.read_float32le(f)
        print(f'Block count: {block_count}, maybe_x_max_block_count: {maybe_x_max_block_count}, maybe_y_max_block_count: {maybe_y_max_block_count},',
              f'global_sidelength: {global_sidelength}, global_xmin: {global_xmin}, global_ymin: {global_ymin}')
        with open(os.path.join(dir, 'hei.ply'), 'wb') as ply:
            ply.write(b'ply\nformat ascii 1.0\nelement vertex ')
            ply.write(f'{block_count * 10 * 10}'.encode('ASCII'))  # All blocks are 10*10
            ply.write(b'\nproperty float x\nproperty float y\nproperty float z\nelement face ')
            ply.write(f'{block_count * 9 * 9}'.encode('ASCII'))  # All blocks have 9*9 quad faces
            ply.write(b'\nproperty list uchar int vertex_index\nend_header\n')
            for _ in range(block_count):
                if Mio.read_fixed_length_string(4, 'ASCII', f) != '1IEH':
                    raise ValueError('Invalid block')
                block_x_entries_count = Mio.read_uint32le(f)
                block_y_entries_count = Mio.read_uint32le(f)
                if block_x_entries_count != 10 or block_y_entries_count != 10:
                    raise ValueError('invalid value for block_*_entries_count')
                block_z_max = Mio.read_float32le(f)
                block_z_min = Mio.read_float32le(f)

                block_z_values = []
                for _ in range(block_y_entries_count):  # always 10
                    for _ in range(block_x_entries_count):  # always 10
                        block_z_values.append(Mio.read_uint8le(f))

                block_x_min = Mio.read_float32le(f)
                if Mio.read_uint32le(f) != 0:  # Skipped, always 0
                    raise ValueError('not 0')
                block_y_min = Mio.read_float32le(f)
                block_x_max = Mio.read_float32le(f)
                if Mio.read_uint32le(f) != 0:  # Skipped, always 0
                    raise ValueError('not 0')
                block_y_max = Mio.read_float32le(f)
                if int(block_x_max - block_x_min) != 60:
                    raise ValueError('Unexpected block width')
                if int(block_y_max - block_y_min) != 60:
                    raise ValueError('Unexpected block depth')
                #print(f'{format(block_z_max, ".2f")}\t{format(block_z_min, ".2f")}\tblock_x_min: {block_x_min}\tblock_y_min: {block_y_min}\tblock_x_max: {block_x_max}\tblock_y_max: {block_y_max}')

                # Calculate data
                for y_entry in range(block_y_entries_count):
                    for x_entry in range(block_x_entries_count):
                        x = block_x_min + (x_entry * (60/9))
                        x = x * -1   # Blender uses a different coordinate system than default Direct X
                        y = block_y_min + (y_entry * (60/9))
                        z = MathUtils.lerp(block_z_min, block_z_max, block_z_values[y_entry * block_y_entries_count + x_entry] / 255)
                        # TODO use numpy to have CORRECT single float precision, the additional precision in Python may be at fault for the small inaccuracies, or the height map have these errors normally
                        ply.write(f'{x} {y} {z}\n'.encode('ASCII'))
            # Add faces as quads (see ply file format)
            number_of_vertices_per_block = 10 * 10  # Always 10 * 10
            for current_block in range(block_count):
                for y in range(9):
                    for x in range(9):
                        first_vertex = (current_block * number_of_vertices_per_block) + (10 * y) + x
                        ply.write(f'4 {first_vertex + 1} {first_vertex} {first_vertex + 10} {first_vertex + 11}\n'.encode('ASCII'))
