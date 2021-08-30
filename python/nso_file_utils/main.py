# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action
import traceback
from os.path import exists

"""
Generate a string based on a template given the variable values passed in
"""
class GenerateTemplateToFile(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        output.result = 'Failed'      
        try:
            with ncs.maapi.single_read_trans(uinfo.username, 'template-manager',
                                             db=ncs.RUNNING) as trans:
                template = ncs.maagic.get_node(trans, kp)
                output_file = input.output_filename
                result = applyVariablesToTemplate(self.log, template, input.variable)
                self.log.debug("Attempting to write file: {}".format(output_file))
                if not exists(output_file) or (exists(output_file) and input.overwrite == True):
                    with open(output_file, 'w') as file:
                        file.write(result)
                elif input.overwrite == False:
                    raise Exception("File exists, please specify overwrite if needed")
        except Exception as error:
            self.log.error(traceback.format_exc())
            result = 'Error {}'.format(error)
            return
        finally:
            output.result =  result

class GenerateTemplate(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        output.result = 'Failed'      
        try:
            with ncs.maapi.single_read_trans(uinfo.username, 'template-manager',
                                             db=ncs.RUNNING) as trans:
                template = ncs.maagic.get_node(trans, kp)
                result = applyVariablesToTemplate(self.log, template, input.variable)
        except Exception as error:
            self.log.error(traceback.format_exc())
            result = 'Error {}'.format(error)
            return
        finally:
            output.result =  result

def applyVariablesToTemplate(log, template, variables):
    """
    Return: String of template with variables applied
    template: Template Node
    variables: Variables Node
    """
    log.info('Processing template {}'.format(template.name))
    result = str(template.source)
    for var in variables:
        log.debug('Processing variable {}'.format(var.name))
        result = result.replace("$"+var.name,var.value)
    return result

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('generate-template', GenerateTemplate)
        self.register_action('generate-template-to-file', GenerateTemplateToFile)
    def teardown(self):
        self.log.info('Main FINISHED')
