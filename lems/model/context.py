"""
Context storage

@author: Gautham Ganapathy
@organization: Textensor (http://textensor.com)
@contact: gautham@textensor.com, gautham@lisphacker.org
"""

from lems.base.base import LEMSBase
from lems.base.errors import ModelError
from lems.model.dynamics import Dynamics
from lems.model.structure import Structure
from lems.model.simulation import Simulation

class Context(LEMSBase):
    """
    Stores the current type and variable context.
    """

    GLOBAL = 0
    """ Global context """

    COMPONENT_TYPE = 1
    """ Component type context """

    COMPONENT = 2
    """ Component context """

    def __init__(self, name, parent = None, context_type = GLOBAL):
        """
        Constructor
        """

        self.name = name
        """ Name identifying this context.
        @type: string """

        self.parent = parent
        """ Reference to parent context.
        @type: lems.model.context.Context """

        self.component_types = {}
        """ Dictionary of component types defined in this conext.
        @type: dict(string -> lems.model.component.ComponentType) """

        self.components = {}
        """ Dictionary of components defined in this context.
        @type: dict(string -> lems.model.component.Component) """

        self.component_refs = {}
        """ Dictionary of component references defined in this context.
        @type: dict(string -> string) """

        self.child_defs = {}
        """ Dictionary of single-instance child object definitions in this
        context.
        @type: dict(string -> string) """

        self.children_defs = {}
        """ Dictionary of multi-instance child objects definitions in this
        context.
        @type: dict(string -> string) """

        self.children = []
        """ List of child objects defined in this context.
        @type: list(lems.model.component.Component) """

        self.parameters = {}
        """ Dictionary of references to parameters defined in this context.
        @type: dict(string -> lems.model.parameter.Parameter) """

        self.context_type = context_type
        """ Context type (Global, component type or component)
        @type: enum(Context.GLOBAL, Context.COMPONENT_TYPE or
        Context.COMPONENT_TYPE) """

        self.dynamics_profiles = {}
        """ Stores the various dynamics profiles of the current object.
        @type: dict(string -> lems.model.dynamics.Dynamics) """

        self.selected_dynamics_profile = None
        """ Name of the dynamics dynamics profile.
        @type: lems.model.dynamics.Dynamics """

        self.exposures = []
        """ List of names of exposed variables.
        @type: list(string) """

        self.requirements = {}
        """ List of names of required variables.
        @type: dict(string -> string) """

        self.texts = {}
        """ Dictionary of text parameters.
        @type: dict(string -> string) """

        self.paths = {}
        """ Dictionary of path parameters.
        @type: dict(string -> string) """

        self.links = {}
        """ Dictionary of link parameters.
        @type: dict(string -> string) """

        self.event_in_ports = []
        """ List of incoming event port names.
        @type: list(string) """

        self.event_out_ports = []
        """ List of outgoing event port names.
        @type: list(string) """

        self.structure = Structure()
        """ Structure object detailing structural aspects of this component.
        @type: lems.model.structure.Structure """

        self.simulation = Simulation()
        """ Simulation object detailing simulation-related aspects of this component.
        @type: lems.model.simulation.Simulation """

        self.attachments = dict()
        """ Dictionary of attachments in this component-type
        @type: dict(string -> string """


    def add_component_type(self, component_type):
        """
        Adds a component type to the list of defined component types in the
        current context.

        @param component_type: Component type to be added
        @type component_type: lems.model.component.ComponentType

        @raise ModelError: Raised when the component type is already defined
        in the current context.
        """

        if component_type.name in self.component_types:
            raise ModelError("Duplicate component type '{0}'".format(\
                component_type.name))

        self.component_types[component_type.name] = component_type

    def add_component(self, component):
        """
        Adds a component to the list of defined components in the current
        context.

        @param component: Component to be added
        @type component: lems.model.component.ComponentType

        @raise ModelError: Raised when the component is already defined in the
        current context.
        """

        if component.id in self.components:
            raise ModelError("Duplicate component '{0}'".format(component.id))

        self.components[component.id] = component

    def add_component_ref(self, name, type):
        """
        Adds a component reference to the list of defined component
        references in the current context.

        @param name: Name of the component reference.
        @type name: string

        @param type: Type of the component reference.
        @type type: string

        @raise ModelError: Raised when the component reference is already
        defined in the current context.
        """

        if name in self.component_refs:
            raise ModelError("Duplicate component reference '{0}'".format(\
                name))

        self.component_refs[name] = type

    def add_child(self, child):
        """
        Adds a child object to the list of child objects in the
        current context.

        @param child: Child object.
        @type child: lems.model.component.Component

        @raise ModelError: Raised when a child is instantiated inside a
        component type.
        """

        if self.context_type == Context.COMPONENT_TYPE:
            raise ModelError("Child definition '{0}' not permitted in "
                             "component type definition '{1}'".format(\
                                 child.id, self.name))

        self.children.append(child)


    def add_child_def(self, name, type):
        """
        Adds a child object definition to the list of single-instance child
        object definitions in the current context.

        @param name: Name of the child object.
        @type name: string

        @param type: Type of the child object.
        @type type: string

        @raise ModelError: Raised when the definition is already in the
        current context.
        """

        if name in self.child_defs:
            raise ModelError("Duplicate child definition '{0}'".format(name))

        self.child_defs[name] = type

    def add_children_def(self, name, type):
        """
        Adds a child object definition to the list of multi-instance child
        object definitions in the current context.

        @param name: Name of the child object.
        @type name: string

        @param type: Type of the child object.
        @type type: string

        @raise ModelError: Raised when the definition is already in the
        current context.
        """

        if name in self.children_defs:
            raise ModelError("Duplicate children definition '{0}'".format(\
                name))

        self.children_defs[name] = type

    def add_parameter(self, parameter):
        """
        Adds a parameter to the list of defined parameters in the current
        context.

        @param parameter: Parameter to be added
        @type parameter: lems.model.parameter.ParameterType

        @raise ModelError: Raised when the parameter is already defined in the
        current context.
        """

        if parameter.name in self.parameters:
            raise ModelError("Duplicate parameter type '{0}'".format(\
                parameter.name))

        self.parameters[parameter.name] = parameter

    def add_dynamics_profile(self, name):
        """
        Adds a dynamics profile to the current context.

        @param name: Name of the dynamics profile.
        @type name: string
        """

        if name in self.dynamics_profiles:
            raise ModelError("Duplicate dynamics profile '{0}'".format(name))

        self.dynamics_profiles[name] = Dynamics(name)
        self.select_dynamics_profile(name)

    def select_dynamics_profile(self, name):
        """
        Selects a dynamics profile by name.

        @param name: Name of the dynamics profile.
        @type name: string

        @raise ModelError: Raised when the specified dynamics profile is
        undefined in the current context.
        """

        if name not in self.dynamics_profiles:
            raise ModelError("Unknown dynamics profile '{0}'".format(name))

        self.selected_dynamics_profile = self.dynamics_profiles[name]

    def add_exposure(self, name):
        """
        Adds a state variable exposure to the current context.

        @param name: Name of the state variable being exposed.
        @type name: string

        @raise ModelError: Raised when the exposure name already exists
        in the current context.

        @raise ModelError: Raised when the exposure name is not
        being defined in the context of a component type.
        """
        if self.context_type != Context.COMPONENT_TYPE:
            raise ModelError("Exposure names can only be defined in "
                             "a component type - '{0}'".format(name))

        if name in self.exposures:
            raise ModelError("Duplicate exposure name '{0}'".format(name))

        self.exposures += [name]

    def add_requirement(self, name, dimension):
        """
        Adds a parameter requirement to the current context.

        @param name: Name of the variable being required.
        @type name: string

        @param name: Dimension of the variable being required.
        @type name: string

        @raise ModelError: Raised when the exposure name already exists
        in the current context.

        @raise ModelError: Raised when the exposure name is not
        being defined in the context of a component type.
        """
        if self.context_type != Context.COMPONENT_TYPE:
            raise ModelError("Requirements can only be defined in "
                             "a component type - '{0}'".format(name))

        if name in self.requirements:
            raise ModelError("Duplicate requirement name '{0}'".format(name))

        self.requirements[name] = dimension

    def add_text_var(self, name, value = None):
        """
        Adds a text variable to the current context.

        @param name: Name of the text variable.
        @type name: string

        @param value: Value of the text variable.
        @type value: string

        @raise ModelError: Raised when the text variable already exists
        in the current context.
        """

        if self.context_type != Context.COMPONENT_TYPE:
            raise ModelError("Text variables can only be defined in "
                             "a component type - '{0}'".format(name))

        if name in self.texts:
            raise ModelError("Duplicate text variable '{0}'".format(name))

        self.texts[name] = value

    def add_path_var(self, name, value = None):
        """
        Adds a path variable to the current context.

        @param name: Name of the path variable.
        @type name: string

        @param value: Value of the path variable.
        @type value: string

        @raise ModelError: Raised when the path variable already exists
        in the current context.
        """

        if self.context_type != Context.COMPONENT_TYPE:
            raise ModelError("Path variables can only be defined in "
                             "a component type - '{0}'".format(name))

        if name in self.paths:
            raise ModelError("Duplicate path variable '{0}'".format(name))

        self.paths[name] = value

    def add_link_var(self, name, type = None):
        """
        Adds a link variable to the current context.

        @param name: Name of the link variable.
        @type name: string

        @param type: Type of the link variable.
        @type type: string

        @raise ModelError: Raised when the link variable already exists
        in the current context.
        """

        if self.context_type != Context.COMPONENT_TYPE:
            raise ModelError("Link variables can only be defined in "
                             "a component type - '{0}'".format(name))

        if name in self.links:
            raise ModelError("Duplicate link variable '{0}'".format(name))

        self.links[name] = type

    def add_event_port(self, name, direction):
        """
        Adds an event port to the list of event ports handled by this
        component or component type.

        @param name: Name of the event port.
        @type name: string

        @param direction: Event direction ('in' or 'out').
        @type direction: string

        @raise ModelError: Raised when the definition is already in the
        current context.
        """

        if name in self.event_in_ports or name in self.event_out_ports:
            raise ModelError("Duplicate event '{0}'".format(name))

        if direction == 'in':
            self.event_in_ports.append(name)
        else:
            self.event_out_ports.append(name)

    def add_attachment(self, name, type_):
        """
        Adds an attachment to this component-type.

        @param name: Name of the attachment.
        @type name: string

        @param type_: Type of the attachment.
        @type type_: string

        @raise ModelError: Raised when the attachment is already in the
        current context.
        """

        if name in self.attachments:
            raise ModelError("Duplicate attachment '{0}'".format(name))

        self.attachments[type_] = name


    def lookup_component_type(self, name):
        """
        Searches the current context and parent contexts for a component type
        with the given name.

        @param name: Name of the component type.
        @type name: string

        @return: Resolved component type object, or None on failure.
        @rtype: lems.model.component.ComponentType
        """

        if name in self.component_types:
            return self.component_types[name]
        elif self.parent:
            return self.parent.lookup_component_type(name)
        else:
            return None

    def lookup_component(self, name):
        """
        Searches the current context and parent contexts for a component
        with the given name.

        @param name: Name of the component.
        @type name: string

        @return: Resolved component object, or None on failure.
        @rtype: lems.model.component.Component
        """

        if name in self.components:
            return self.components[name]
        elif self.parent:
            return self.parent.lookup_component(name)
        else:
            return None

    def lookup_component_ref(self, name):
        """
        Searches the current context and parent contexts for a component
        with the given name.

        @param name: Name of the component.
        @type name: string

        @return: Resolved component object, or None on failure.
        @rtype: lems.model.component.Component
        """

        if name in self.component_refs:
            cname = self.component_refs[name]
            return self.lookup_component(cname)
        elif self.parent:
            return self.parent.lookup_component_ref(name)
        else:
            return None

    def lookup_child(self, name):
        """
        Searches the current context and parent contexts for a child
        with the given name.

        @param name: Name of the component.
        @type name: string

        @return: Component type for the child, or None on failure.
        @rtype: string
        """

        if name in self.child_defs:
            return self.child_defs[name]
        elif self.parent:
            return self.parent.lookup_child(name)
        else:
            return None


    def lookup_parameter(self, parameter_name):
        """
        Looks up a parameter by name within this context.

        @param parameter_name: Name of the parameter.
        @type parameter_name: string

        @return: Corresponding Parameter object or None if not found.
        @rtype: lems.model.parameter.Parameter
        """

        if parameter_name in self.parameters:
            return self.parameters[parameter_name]
        else:
            return None

    def lookup_path_parameter(self, path_name):
        """
        Looks up a path parameter.

        @param path_name: Name of the path parameter.
        @type parameter_name: string

        @return: Value of the path parameter
        @rtype: string
        """

        path_param = self.lookup_parameter(path_name)
        if path_param == None or path_param.dimension != '__path__':
            return None
        else:
            return path_param.value

    def lookup_text_parameter(self, text_name):
        """
        Looks up a text parameter.

        @param text_name: Name of the text parameter.
        @type parameter_name: string

        @return: Value of the text parameter
        @rtype: string
        """

        text_param = self.lookup_parameter(text_name)
        if text_param == None or text_param.dimension != '__text__':
            return None
        else:
            return text_param.value

class Contextual(LEMSBase):
    """
    Base class for objects that need to store their own context.
    """

    def __init__(self, name, parent = None, context_type = Context.GLOBAL):
        """
        Constructor.
        """

        self.context = Context(name, parent, context_type)
        """ Context object.
        @type: lems.model.context.Context """

    def add_component_type(self, component_type):
        """
        Adds a component type to the list of defined component types in the
        current context.

        @param component_type: Component type to be added
        @type component_type: lems.model.component.ComponentType
        """

        self.context.add_component_type(component_type)

    def add_component(self, component):
        """
        Adds a component to the list of defined components in the current
        context.

        @param component: Component to be added
        @type component: lems.model.component.Component
        """

        self.context.add_component(component)

    def add_parameter(self, parameter):
        """
        Adds a parameter to the list of defined parameters in the current
        context.

        @param parameter: Parameter to be added
        @type parameter: lems.model.parameter.Parameter
        """

        self.context.add_parameter(parameter)

    def lookup_parameter(self, parameter_name):
        """
        Lookup a parameter in this context by name.

        @param parameter_name: Name of the parameter.
        @type parameter_name: string

        @return: Corresponding Parameter object or None if not found.
        @rtype: lems.model.parameter.Parameter
        """

        return self.context.lookup_parameter(parameter_name)
