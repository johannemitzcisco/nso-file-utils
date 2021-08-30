# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.dp import Action
import traceback

class GenerateTemplate(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        output.result = 'Failed'      
        try:
            with ncs.maapi.single_read_trans(uinfo.username, 'template-manager',
                                             db=ncs.RUNNING) as trans:
                template = ncs.maagic.get_node(trans, kp)
                self.log.info('Processing template {}'.format(template.name))
                result = str(template.source)
                for var in input.variable:
                    self.log.debug('Processing variable {}'.format(var.name))
                    result = result.replace("$"+var.name,var.value)
        except Exception as error:
            self.log.error(traceback.format_exc())
            result = 'Error {}'.format(error)
            return
        finally:
            output.result =  result

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('generate-template', GenerateTemplate)
    def teardown(self):
        self.log.info('Main FINISHED')
