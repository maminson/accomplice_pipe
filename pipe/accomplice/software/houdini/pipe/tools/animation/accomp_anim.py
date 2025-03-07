""" This file contains the code for the accomp_anim HDA """

# Imports
import hou
import os, functools
import re
import glob
from pipe.shared.object import Asset
from pipe.shared.helper.utilities.houdini_utils import HoudiniUtils
import pipe

from pipe.shared.helper.utilities.optimization_utils import DataCache

data_cache = DataCache()


# Constants
ANIM_SUBDIRECTORY = 'anim'
EXTENSION = '.usd'

# Functions
class AnimationImporter():

    def __init__(self):
        print("IMPORTING ANIMATION")
        self.shot = self.get_shot()
        print("shot: ", self.shot.name)

    def get_shot(self):
        shot_name = HoudiniUtils.get_shot_name()
        # shot = pipe.server.get_shot(shot_name)
        shot = data_cache.retrieve_from_cache(shot_name, pipe.server.get_shot, shot_name)
        return shot

    def get_character_options_list(self):
        # self.shot = pipe.server.get_shot(HoudiniUtils.get_shot_name())
        if self.shot is None:
            self.shot = self.get_shot()
        print('This is the shot name!', self.shot.name)

        # Check if the current directory has an anim folder
        anim_dir = self.shot.get_shotfile_folder('anim')

        if not os.path.isdir(anim_dir): # Error check
            hou.ui.displayMessage("There doesn't seem to be an anim folder in the context of this file. Contact pipe engineer.")
            return []

        path_to_check = os.path.join(anim_dir, '**', '*' + EXTENSION)
        display_list = []
        for file in glob.iglob(path_to_check, recursive=True): # For each file in the anim directory
            if not 'anim_backup' in file:
                # Get the file name, not the full path
                character_name = os.path.basename(file).replace(EXTENSION, '').title()
                display_list.append(file)
                display_list.append(character_name)

        return display_list

    def is_character(self, name: str) -> bool:
        lower_name = name.lower()
        return lower_name in ['letty', 'ed', 'vaughn']

    def get_anim_name(self, node):
        return node.parm('./anim_name').eval()

    def get_asset_name(self, node):
        return node.parm('./asset_name').eval()

    def get_anim_description(self, node):
        return node.parm('./anim_descr').eval()

    # Called when a new character/object name is selected
    def animation_name_update(self, node):
        anim_path = node.parm('./anim_filename').eval() # Get path to file
        print("anim path: ", anim_path)

        anim_name = os.path.basename(anim_path).replace(EXTENSION, '') # Get just the name of the file, excluding extension
        #Couldn't find a use for this at the moment, making it hard to get the constructionsign into the scenes.
        '''anim_name_components = anim_name.split('_')
        if len(anim_name_components) > 1:
            asset_name = anim_name_components[0]
            anim_description = anim_name_components[1]
        else:'''
        asset_name = re.sub(r'[0-9]+', '', anim_name)
        anim_description = ''

        print("anim name ", anim_name)
        print("asset name: ", asset_name)

        node.parm('./anim_name').set(anim_name)
        node.parm('./asset_name').set(asset_name)
        node.parm('./anim_descr').set(anim_description)
        
        # triggers a script in the character materials node
        # I don't think this is needed anymore now that the character name is set by parameter reference.
        materials_node = node.node('Materials')
        #if materials_node != None and materials_node != '':
            #materials_node.parm('character').set(asset_name)
            #materials_node.hdaModule().set_character(materials_node)

        node.allowEditingOfContents()
        self.set_anim_type(node)

    def set_anim_type(self, node):
        anim_type = node.parm('anim_type')
        asset_name = self.get_asset_name(node)
        fx_enabled = node.parm('fx_enabled')
        if self.is_character(asset_name):
            anim_type.set('human')
            fx_enabled.set(1)
        else:
            anim_type.set('object')
            fx_enabled.set(0)

    def prune(self, node):
        # Make prim path list
        primive_paths = []
        if (node.parm('hidetemphair').eval() == 1):
            if (node.parm('anim_type').eval() == 'human'):
                primive_paths.append('/anim/`chs("../asset_name")`/geo/temp_hair')
                
        if (node.parm('hidetempcloth').eval() == 1) and (node.parm('anim_type').eval() == 'human'):
            primive_paths.append('/anim/`chs("../asset_name")`/geo/temp_clothing')
            
        if (node.parm('hidefxgeo').eval() == 1) and (node.parm('fx_enabled').eval() == 1):
            primive_paths.append('/anim/`chs("../asset_name")`/geo/fx')
        
        # Set prim path in the prune node
        prune = node.node('display_settings_prune')
        prune.parm('num_rules').set(len(primive_paths))

        for i, primitive_path in enumerate(primive_paths, start=1):
            parameter_name = f'primpattern{i}'
            prune.parm(parameter_name).set(primitive_path)