class ExperimentorException(Exception):
    pass

class ModelDefinitionException(ExperimentorException):
    pass

class ExperimentDefinitionException(ExperimentorException):
    pass

class DuplicatedParameter(ExperimentorException):
    pass