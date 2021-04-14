import os
import pydoc
import re

import html2text
import m2r

from imswitch.imcommon import prepareApp, constants
from imswitch.imcommon.controller import ModuleCommunicationChannel
from imswitch.imcommon.view import MultiModuleWindow
from imswitch.imscripting.model.actions import _Actions

from imswitch import imcontrol, imreconstruct


def writeDocs(cls):
    obj, name = pydoc.resolve(cls)
    html = pydoc.html.page(pydoc.describe(obj), pydoc.html.document(obj, name))

    markdown = html2text.html2text(html)
    markdown = markdown.replace('`', '')
    markdown = re.sub(r'^[ \t|]+', '', markdown, flags=re.MULTILINE)

    rst = m2r.convert(markdown)

    with open(os.path.join(apiDocsDir, f'{cls.__name__}.rst'), 'w') as file:
        file.write(rst)


# Create and set working directory
docsDir = os.path.join(constants.rootFolderPath, 'docs')
apiDocsDir = os.path.join(docsDir, 'api')
os.makedirs(apiDocsDir, exist_ok=True)

# Generate docs for modules
dummyApp = prepareApp()
dummyModuleCommChannel = ModuleCommunicationChannel()

modules = [imcontrol, imreconstruct]  # imscripting excluded
for modulePackage in modules:
    _, mainController = modulePackage.getMainViewAndController(dummyModuleCommChannel)
    if not hasattr(mainController, 'api'):
        continue

    moduleId = modulePackage.__name__
    moduleId = moduleId[moduleId.rindex('.') + 1:]
    moduleId = f'api.{moduleId}'

    class API:
        pass

    API.__name__ = moduleId
    API.__doc__ = f""" These functions are available in the {moduleId} object. """

    for key, value in mainController.api.items():
        setattr(API, key, value)

    writeDocs(API)

dummyApp.exit(0)

# Generate docs for actions
class _actions:
    """ These functions are available at the global level. """
    pass

for subObjName in dir(_Actions):
    subObj = getattr(_Actions, subObjName)
    if hasattr(subObj, '_APIExport') and subObj._APIExport:
        setattr(_actions, subObjName, subObj)

writeDocs(_actions)

# Generate docs for mainWindow
class mainWindow:
    """ These functions are available in the mainWindow object. """
    pass

for subObjName in dir(MultiModuleWindow):
    subObj = getattr(MultiModuleWindow, subObjName)
    if hasattr(subObj, '_APIExport') and subObj._APIExport:
        setattr(mainWindow, subObjName, subObj)

writeDocs(mainWindow)


# Copyright (C) 2020, 2021 TestaLab
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
