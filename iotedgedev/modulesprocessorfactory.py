
from .dotnetmoduleprocessor import DotNetModuleProcessor
from .othermoduleprocessor import OtherModuleProcessor

class ModulesProcessorFactory(object):

    def __init__(self, envvars, utility, output):#, module_language):
        self.envvars = envvars
        self.utility = utility
        self.output = output
 
    def get(self, module_language):
        module_language = module_language.lower()
        if module_language == "csharp" or module_language == "fsharp" or module_language == "vbasic":
            return DotNetModuleProcessor(self.envvars, self.utility, self.output)#, "")

        else:
            return OtherModuleProcessor()#self.envvars, self.utility, self.output, "")