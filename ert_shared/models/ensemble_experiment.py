from res.enkf.enums import HookRuntime
from res.enkf import ErtRunContext, EnkfSimulationRunner

from ert_shared.models import BaseRunModel
from ert_shared import ERT

class EnsembleExperiment(BaseRunModel):

    def __init__(self):
        super(EnsembleExperiment, self).__init__(ERT.enkf_facade.get_queue_config())

    def runSimulations__(self, arguments, run_msg):

        self._job_queue = self._queue_config.create_job_queue( )
        run_context = self.create_context( arguments )

        self.setPhase(0, "Running simulations...", indeterminate=False)

        self.setPhaseName("Pre processing...", indeterminate=True)
        self.ert().getEnkfSimulationRunner().createRunPath( run_context )
        EnkfSimulationRunner.runWorkflows(HookRuntime.PRE_SIMULATION, ERT.ert)

        self.setPhaseName( run_msg, indeterminate=False)

        num_successful_realizations = self.ert().getEnkfSimulationRunner().runEnsembleExperiment(self._job_queue, run_context)

        num_successful_realizations += arguments.get('prev_successful_realizations', 0)
        self.checkHaveSufficientRealizations(num_successful_realizations)

        self.setPhaseName("Post processing...", indeterminate=True)
        EnkfSimulationRunner.runWorkflows(HookRuntime.POST_SIMULATION, ERT.ert)
        self.setPhase(1, "Simulations completed.") # done...

        return run_context


    def runSimulations(self, arguments):
        return self.runSimulations__(  arguments , "Running ensemble experiment...")


    def create_context(self, arguments):
        fs_manager = self.ert().getEnkfFsManager()
        result_fs = fs_manager.getCurrentFileSystem( )

        model_config = self.ert().getModelConfig( )
        runpath_fmt = model_config.getRunpathFormat( )
        jobname_fmt = model_config.getJobnameFormat( )
        subst_list = self.ert().getDataKW( )
        itr = 0
        mask = arguments["active_realizations"]

        run_context = ErtRunContext.ensemble_experiment(result_fs,
                                                        mask,
                                                        runpath_fmt,
                                                        jobname_fmt,
                                                        subst_list,
                                                        itr)
        self._run_context = run_context
        self._last_run_iteration = run_context.get_iter()
        return run_context

    @classmethod
    def name(cls):
        return "Ensemble Experiment"