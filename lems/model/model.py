"""
Model storage

@author: Gautham Ganapathy
@organization: Textensor (http://textensor.com)
@contact: gautham@textensor.com, gautham@lisphacker.org
"""

from lems.base.errors import ModelError
from lems.model.context import Contextual
from lems.model.parameter import Parameter

import re
import copy

class Model(Contextual):
    """
    Store the model read from a LEMS file.
    """

    def __init__(self):
        """
        Constructor.
        """

        super(Model, self).__init__('__model__')
        
        self.targets = []
        """ Names of simulations to run.
        @type: string """

        self.dimensions = None
        """ Dictionary of references to dimensions defined in the model.
        @type: dict(string -> lems.model.simple.Dimension) """

        self.units = None
        """ Dictionary of references to units defined in the model.
        @type: dict(string -> lems.model.simple.Unit) """

        self.context = None
        """ Global (root) context.
        @type: lems.model.context.Context """

        self.next_free_id = -1
        """ Number used to create a new ID.
        @type: Integer """


    def add_target(self, target):
        """
        Add the name of the component to run to the list of components to
        run by default.
        
        @param target: Name of a simulation to run by default
        @type target: string """
        self.targets += [target]

    def add_dimension(self, dimension):
        """
        Adds a dimension to the list of defined dimensions.

        @param dimension: Dimension to be added to the model.
        @type dimension: lems.base.units.Dimension

        @raise ModelError: Raised when the dimension is already defined.
        """

        if self.dimensions == None:
            self.dimensions = dict()

        if dimension.name in self.dimensions:
            self.raise_error('Duplicate dimension - ' + dimension.name,
                             self.context)
        else:
            self.dimensions[dimension.name] = dimension
        
    def add_unit(self, unit):
        """
        Adds a unit to the list of defined units.

        @param unit: Unit to be added to the model.
        @type unit: lems.base.units.Unit

        @raise ModelError: Raised when the unit is already defined.
        """

        if self.units == None:
            self.units = dict()

        if unit.symbol in self.units:
            self.raise_error('Duplicate unit - ' + unit.symbol, self.context)
        else:
            self.units[unit.symbol] = unit

    def resolve_parameter_value(self, parameter, context):
        """
        Resolves the numeric value of a parameter based on the given value
        in terms of the symbols and dimensions defined in the model.

        @param parameter: Parameter object to be resolved.
        @type parameter: lems.model.parameter.Parameter

        @param context: Context containing the parameter
        @type context: lems.model.context.Context

        @raise ModelError: Raised when the value of the parameter is not set.

        @raise ModelError: Raised when the unit symbol does not match the
        parameter's dimension.

        @raise ModelError: Raised when the unit symbol is undefined.
        """
        
        if parameter.value == None:
            self.raise_error('Parameter {0} not initialized'.format(\
                parameter.name), context)

        number = float(re.split('[a-zA-z]+', parameter.value)[0].strip())
        sym = re.split('[^a-zA-z]+', parameter.value)[1].strip()

        if sym == '':
            parameter.numeric_value = number
        else:
            if sym in self.units:
                unit = self.units[sym]
                if parameter.dimension != unit.dimension:
                    if parameter.dimension == '*':
                        parameter.dimension = unit.dimension
                    else:
                        self.raise_error(('Unit symbol {0} cannot '
                                         'be used for dimension {1}').format(\
                                             sym, parameter.dimension),
                                         context)
                parameter.numeric_value = number * (10 ** unit.pow10)
            else:
                self.raise_error('Unknown unit symbol {0}'.format(sym),
                                 context)

    def resolve_extended_component_type(self, context, component_type):
        """
        Resolves the specified component type's parameters from it's base
        component type.

        @param context: Context object containing the component type.
        @type context: lems.model.context.Context

        @param component_type: Component type to be resolved.
        @type component_type: lems.model.component.ComponentType

        @raise ModelError: Raised when the base component type cannot be
        resolved.

        @raise ModelError: Raised when a parameter in the base component type
        is redefined in this component type.
        """
        
        base_type = context.lookup_component_type(component_type.extends)
        if base_type == None:
            self.raise_error('Base type {0} not found for component type {1}'.
                             format(component_type.extends,
                                    component_type.name),
                             context)
        if base_type.extends:
            self.resolve_extended_component_type(context, base_type)

        this_context = component_type.context
        base_context = base_type.context

        for pn in base_context.parameters:
            if pn in this_context.parameters:
                pt = this_context.parameters[pn]

                if pt.dimension == '__dimension_inherited__':
                    pb = base_context.parameters[pn]
                    this_context.parameters[pn] = Parameter(pt.name,
                                                            pb.dimension,
                                                            pt.fixed,
                                                            pt.value)
                else:
                    self.raise_error(('Parameter {0} in {1} is redefined ' +
                                     'in {2}').format(pn, base_type.name,
                                                      component_type.name),
                                     context)
            else:
                this_context.parameters[pn] = base_context.parameters[pn].\
                                              copy()

        this_context.requirements = copy.copy(base_context.requirements)

        component_type.extends = None

    def resolve_extended_component(self, context, component):
        """
        Resolves the specified component's parameters from it's base
        component.

        @param context: Context object containing the component.
        @type context: lems.model.context.Context

        @param component: Component to be resolved.
        @type component: lems.model.component.Component

        @raise ModelError: Raised when the base component cannot be
        resolved.

        @raise ModelError: Raised when a parameter in the base component
        is redefined in this component.

        @note: Consider changing Component.id to Component.name and merging
        this method with resolve_extended_component_type.
        """
        
        base = context.lookup_component(component.extends)
        if base == None:
            self.raise_error('Base component {0} not found for component {1}'.
                             format(component.extends,
                                    component.id),
                             context)
        if base.extends:
            self.resolve_extended_component(context, base)

        this_context = component.context
        base_context = base.context

        for pn in base_context.parameters:
            if pn in this_context.parameters:
                pt = this_context.parameters[pn]

                if pt.dimension == '__dimension_inherited__':
                    pb = base_context.parameters[pn]
                    this_context.parameters[pn] = Parameter(pt.name,
                                                            pb.dimension,
                                                            pt.fixed,
                                                            pt.value)
                else:
                    self.raise_error(('Parameter {0} in {1} is redefined '
                                     'in {2}').format(pn, base_type.name,
                                                      component_type.name),
                                     context)
            else:
                this_context.parameters[pn] = base_context.parameters[pn].\
                                              copy()

        component.component_type = base.component_type

        this_context.requirements = copy.copy(base_context.requirements)

        component.extends = None

    def resolve_component_structure_from_type(self,
                                              comp_context,
                                              type_context,
                                              component):
        """
        Resolves the specified component's structure from component type.

        @param comp_context: Component's context object.
        @type comp_context: lems.model.context.Context

        @param type_context: Component type's context object.
        @type type_context: lems.model.context.Context

        @param component: Component to be resolved.
        @type component: lems.model.component.Component

        @raise ModelError: Raised when the component type cannot be
        resolved.
        """

        comp_str = comp_context.structure
        type_str = type_context.structure
        
        comp_str.event_connections = type_str.event_connections

        for c in type_str.single_child_defs:
            if c in comp_context.component_refs:
                comp_str.add_single_child_def(c)
            else:
                raise ModelError("Trying to multi-instantiate from an "
                                 "invalid component reference '{0}'".format(\
                        c))

        for c in type_str.multi_child_defs:
            n = type_str.multi_child_defs[c]
            if c in comp_context.component_refs:
                component = comp_context.component_refs[c]
                if n in comp_context.parameters:
                    number = int(comp_context.parameters[n].numeric_value)
                    comp_str.add_multi_child_def(component, number)
                else:
                    raise ModelError("Trying to multi-instantiate using an "
                                     "invalid number parameter '{0}'".\
                                     format(n))
            else:
                raise ModelError("Trying to multi-instantiate from an "
                                 "invalid component reference '{0}'".format(\
                                     c))

        comp_str.foreach = type_str.foreach


    def resolve_component_from_type(self, context, component):
        """
        Resolves the specified component's parameters from component type.

        @param context: Context object containing the component.
        @type context: lems.model.context.Context

        @param component: Component to be resolved.
        @type component: lems.model.component.Component

        @raise ModelError: Raised when the component type cannot be
        resolved.
        """

        component_type = context.lookup_component_type(
            component.component_type)
            
        if component_type == None:
            self.raise_error('Type {0} not found for component {1}'.
                             format(component.component_type,
                                    component.id),
                             context)

        this_context = component.context
        type_context = component_type.context

        for pn in type_context.parameters:
            pt = type_context.parameters[pn]
            if pn in this_context.parameters:
                pc = this_context.parameters[pn]

                if pc.value:
                    value = pc.value
                else:
                    value = pt.value
                    
                if pc.dimension == '__dimension_inherited__':
                    if pt.fixed:
                        np = Parameter(pn, pt.dimension, pt.fixed, value)
                    else:
                        np = Parameter(pn, pt.dimension, pc.fixed, value)
                    this_context.parameters[pn] = np
            else:
                this_context.parameters[pn] = pt.copy()

            self.resolve_parameter_value(this_context.parameters[pn],
                                         this_context)

        for pn in this_context.parameters:
            pc = this_context.parameters[pn]
            if pc.dimension == '__dimension_inherited__':
                if pn in type_context.texts:
                    pc.dimension = '__text__'
                    this_context.texts[pn] = type_context.texts[pn]
                elif pn in type_context.paths:
                    pc.dimension = '__path__'
                    this_context.paths[pn] = type_context.paths[pn]
                elif pn in type_context.links:
                    pc.dimension = '__link__'
                    this_context.links[pn] = type_context.links[pn]
                elif pn in type_context.component_refs:
                    pc.dimension = '__component_ref__'
                    cf = type_context.component_refs[pn]
                    this_context.component_refs[pn] = pc.value

        for dpn in type_context.dynamics_profiles:
            dp = type_context.dynamics_profiles[dpn].copy()
            this_context.dynamics_profiles[dpn] = dp
                
            if dpn == type_context.selected_dynamics_profile.name:
                this_context.selected_dynamics_profile = dp

        this_context.simulation = type_context.simulation.copy()
                    
        for port in type_context.event_in_ports:
            this_context.event_in_ports.append(port)
        for port in type_context.event_out_ports:
            this_context.event_out_ports.append(port)

        self.resolve_component_structure_from_type(this_context,
                                                   type_context,
                                                   component)

        this_context.children_defs = copy.copy(type_context.children_defs)

        this_context.requirements = copy.copy(type_context.requirements)

    def resolve_regime(self, context, regime):
        """
        Resolves name references in the given dynamics regime to actual
        objects.

        @param context: Current context.
        @type context: lems.model.context.Context

        @param regime: Dynamics regime to be resolved.
        @type regime: lems.model.dynamics.Dynamics

        @raise ModelError: Raised when the quantity to be recorded is not a
        path.

        @raise ModelError: Raised when the color specified is not a text
        entity.
        """

        pass

    def resolve_simulation(self, context):
        """
        Resolves simulation specifications in a component-type context.

        @param context: Current context.
        @type context: lems.model.context.Context

        @raise ModelError: Raised when the quantity to be recorded is not a
        path.

        @raise ModelError: Raised when the color specified is not a text
        entity.
        """

        simulation = context.simulation

        # Resolve record statements
        for idx in simulation.records:
            record = simulation.records[idx]

            if record.quantity in context.parameters and \
               record.scale in context.parameters and \
               record.color in context.parameters:
                qp = context.parameters[record.quantity]
                sp = context.parameters[record.scale]
                cp = context.parameters[record.color]

                if qp.dimension != '__path__':
                    self.raise_error('<Record>: The quantity to be recorded'
                                     'must be a path',
                                     context)
                if cp.dimension != '__text__':
                    self.raise_error('<Record>: The color to be used must be '
                                     'a reference to a text variable',
                                     context)
                record.quantity = qp.value
                record.scale = sp.value
                record.color = cp.value
                record.numeric_scale = sp.numeric_value




    def resolve_dynamics_profile(self, context, dynamics):
        """
        Resolves name references in the given dynamics profile to actual
        objects.

        @param context: Current context.
        @type context: lems.model.context.Context

        @param dynamics: Dynamics profile to be resolved.
        @type dynamics: lems.model.dynamics.Dynamics
        """

        self.resolve_regime(context, dynamics.default_regime)
        
        for rn in dynamics.regimes:
            self.resolve_regime(context, regime)
            
    def resolve_component(self, context, component):
        """
        Resolves the specified component.

        @param context: Context object containing the component.
        @type context: lems.model.context.Context

        @param component: Component to be resolved.
        @type component: lems.model.component.Component

        @raise ModelError: Raised when the dimension for a parameter cannot
        be resolved.
        """

        self.resolve_context(component.context)
        if component.extends:
            self.resolve_extended_component(context, component)
        self.resolve_component_from_type(context, component)
        for pn in component.context.parameters:
            p = component.context.parameters[pn]
            if p.dimension == '__dimension_inherited__':
                self.raise_error(('The dimension for parameter {0} in '
                                  'component {1} could not be resolved').\
                                 format(pn, component.id),
                                 component.context)

        # Resolve dynamics
        for dpn in component.context.dynamics_profiles:
            dp = component.context.dynamics_profiles[dpn]
            self.resolve_dynamics_profile(component.context, dp)

    def resolve_child(self, context, child):
        """
        Resolves the specified child component.

        @param context: Context object containing the component.
        @type context: lems.model.context.Context

        @param child: Child component to be resolved.
        @type child: lems.model.component.Component

        @raise ModelError: Raised when the parent component cannot be
        resolved.

        @raise ModelError: Raised when the component type for the parent
        component cannot be resolved.
        """

        parent = context.lookup_component(context.name)
        if parent == None:
            self.raise_error('Unable to resolve component \'{0}\''.\
                             format(context.name))
        parent_type = context.lookup_component_type(parent.component_type)
        if parent_type == None:
            self.raise_error('Unable to resolve component type \'{0}\''.\
                             format(parent.component_type))

        ptctx = parent_type.context

        if child.id in ptctx.child_defs:
            if child.component_type == '__type_inherited__':
                child.component_type = ptctx.child_defs[child.id]
            #else:
            #    print child.id, child.component_type
            #    raise Exception('TODO')
            context.add_component(child)
        else:
            for cdn in ptctx.children_defs:
                cdt = ptctx.children_defs[cdn]

                if child.id == cdt:
                    child.component_type = cdt
                    child.id = self.make_id()
                    context.add_component(child)
                    if cdn not in context.children_defs:
                        context.add_children_def(cdn, cdt)
                    break
                elif child.component_type == cdt:
                    context.add_component(child)
                    if cdn not in context.children_defs:
                        context.add_children_def(cdn, cdt)
                    break

    def resolve_context(self, context):
        """
        Resolves name references in the given context to actual objects.

        @param context: Context to be resolved.
        @type context: lems.model.context.Context

        @raise ModelError: Raised when the dimension for a parameter cannot
        be resolved.
        """
        
        # Resolve component-types
        for ctn in context.component_types:
            component_type = context.component_types[ctn]
            self.resolve_context(component_type.context)
            if component_type.extends:
                self.resolve_extended_component_type(context, component_type)
            
        # Resolve children
        if context.children:
            for child in context.children:
                self.resolve_child(context, child)

        # Resolve components
        for cid in context.components:
            component = context.components[cid]
            self.resolve_component(context, component)
            self.resolve_simulation(component.context)


    def resolve_model(self):
        """
        Resolves name references in the model to actual objects.

        @raise ModelError: Raised when the dimension for a given unit cannot
        be resolved.
        """
        
        # Verify dimensions for units
        for symbol in self.units:
            dimension = self.units[symbol].dimension
            if dimension not in self.dimensions:
                self.raise_error('Dimension {0} not defined for unit {1}'\
                                 .format(dimension, symbol),
                                 self.context)

        # Resolve global context
        self.resolve_context(self.context)

    def raise_error(self, message, context):
        s = 'Caught ModelError in lems'

        context_name_stack = []
        while context != None:
            context_name_stack.insert(0, context.name)
            context = context.parent

        for context_name in context_name_stack:
            s += '.' + context_name
            
        s += ':\n  ' + message

        raise ModelError(s)

    def make_id(self):
        self.next_free_id = self.next_free_id + 1
        return 'id#{0}'.format(self.next_free_id)
        
    
    #####################################################################33

    tab = '    '

    def regime2str(self, regime, prefix):
        s = ''
        if regime.state_variables:
            s += prefix + Model.tab + 'State variables:\n'
            for svn in regime.state_variables:
                sv = regime.state_variables[svn]
                s += prefix + Model.tab*2 + sv.name
                if sv.exposure:
                    s += ' (exposed as ' + sv.exposure + ')'
                s += ': ' + sv.dimension + '\n'

        if regime.time_derivatives:
            s += prefix + Model.tab + 'Time derivatives:\n'
            for tdv in regime.time_derivatives:
                td = regime.time_derivatives[tdv]
                s += prefix + Model.tab*2 + td.variable + ' = ' + td.value\
                     + ' | ' + str(td.expression_tree) + '\n'

        if regime.derived_variables:
            s += prefix + Model.tab + 'Derived variables:\n'
            for dvn in regime.derived_variables:
                dv = regime.derived_variables[dvn]
                s += prefix + Model.tab*2 + dv.name 
                if dv.value:
                    s += ' = ' + dv.value + ' | ' + str(dv.expression_tree) + '\n'
                else:
                    s += '\n'


        if regime.event_handlers:
            s += prefix + Model.tab + 'Event Handlers:\n'
            for eh in regime.event_handlers:
                s += prefix + Model.tab*2 + str(eh) + '\n'
                if eh.actions:
                    s += prefix + Model.tab*3 + 'Actions:\n'
                    for a in eh.actions:
                        s += prefix + Model.tab*4 + str(a) + '\n'

        return s
    
    def dynamics2str(self, dynamics, prefix):
        s = prefix
        if dynamics.name != '':
            s += name
        else:
            s += '*'
        s += '\n'

        if dynamics.default_regime:
            s += prefix + Model.tab + 'Default regime:\n'
            s += self.regime2str(dynamics.default_regime,
                                 prefix + Model.tab)

        return s

    def structure2str(self, structure, prefix):
        s = prefix + 'Structure:\n'

        if structure.event_connections:
            s += prefix + Model.tab + 'Event connections:\n'
            for conn in structure.event_connections:
                (from_, fromport, to, toport) = conn
                s += prefix + Model.tab*2 + '{0}:{1} -> {2}:{3}\n'.format(\
                    from_, fromport, to, toport)

        if structure.single_child_defs:
            s += prefix + Model.tab + 'Single child instantiations:\n'
            for c in structure.single_child_defs:
                s += prefix + Model.tab*2 + c + '\n'

        if structure.multi_child_defs:
            s += prefix + Model.tab + 'Multi child instantiations:\n'
            for c in structure.multi_child_defs:
                s += prefix + Model.tab*2 + '{0} * {1}\n'.format(\
                    c, structure.multi_child_defs[c])

        if structure.foreach:
            s += prefix + Model.tab + 'ForEach:\n'
            for fe in structure.foreach:
                s += prefix + Model.tab*2 + 'ForEach {0} as {1}\n'.format(\
                    fe.target, fe.name)
                s += self.structure2str(fe, prefix + Model.tab*3)
                

                
        return s

    def simulation2str(self, simulation, prefix):
        s = prefix + 'Simulation Specs:\n'
        prefix = prefix + Model.tab

        if simulation.runs:
            s += prefix + 'Runs:\n'
            for rn in simulation.runs:
                r = simulation.runs[rn]
                s += '{0}{1} {2} {3} {4}\n'.format(prefix + Model.tab,
                                                   r.component,
                                                   r.variable,
                                                   r.increment,
                                                   r.total)

        if simulation.records:
            s += prefix + 'Recordings:\n'
            for q in simulation.records:
                r = simulation.records[q]
                s += '{0}{1} {2} {3}\n'.format(prefix + Model.tab,
                                                   r.quantity,
                                                   r.scale,
                                                   r.color)

        if simulation.data_displays:
            s += prefix + 'Data displays:\n'
            for t in simulation.data_displays:
                r = simulation.data_displays[t]
                s += '{0}{1} {2}\n'.format(prefix + Model.tab,
                                                   t, r)

        return s


    def context2str(self, context, prefix):
        s = ''
        prefix = prefix + Model.tab
        if context.component_types:
            s += prefix + 'Component types:\n'
            for tn in context.component_types:
                t = context.component_types[tn]
                s += prefix + Model.tab + t.name
                if t.extends:
                    s += ' (extends ' + t.extends + ')'
                s += '\n'
                s += self.context2str(t.context, prefix + Model.tab)

        if context.components:
            s += prefix + 'Components:\n'
            for cn in context.components:
                c = context.components[cn]
                s += prefix + Model.tab + c.id
                if c.component_type:
                    s += ': ' + c.component_type + '\n'
                else:
                    s+= ' (extends ' + c.extends + ')' + '\n'
                s += self.context2str(c.context, prefix + Model.tab)

        if context.component_refs:
            s += prefix + 'Component references:\n'
            for cref in context.component_refs:
                t = context.component_refs[cref]
                s += prefix + Model.tab + cref + ': ' + t + '\n'

        if context.child_defs:
            s += prefix + 'Child definitions:\n'
            for cref in context.child_defs:
                t = context.child_defs[cref]
                s += prefix + Model.tab + cref + ': ' + t + '\n'

        if context.children_defs:
            s += prefix + 'Children definitions:\n'
            for cref in context.children_defs:
                t = context.children_defs[cref]
                s += prefix + Model.tab + cref + ': ' + t + '\n'

        if context.children:
            s += prefix + 'Children:\n'
            for child in context.children:
                s += prefix + Model.tab + child.id + ': ' + \
                     child.component_type + '\n'
                s += self.context2str(child.context, prefix + Model.tab)

        if context.parameters:
            s += prefix + 'Parameters:\n'
            for pn in context.parameters:
                p = context.parameters[pn]
                s += prefix + Model.tab + p.name
                s += ': ' + p.dimension
                if p.value:
                    s += ': ' + str(p.value)
                    if p.fixed:
                        s += ' (fixed)'
                if p.numeric_value:
                    s += ' - ' + str(p.numeric_value)
                s += '\n'

        if context.exposures:
            s += prefix + 'Exposures:\n'
            for name in context.exposures:
                s += prefix + Model.tab + name + '\n'

        if context.texts:
            s += prefix + 'Text variables:\n'
            for name in context.texts:
                value = context.texts[name]
                s += prefix + Model.tab + name
                if value:
                    s += ': ' + value + '\n'
                else:
                    s += '\n'

        if context.paths:
            s += prefix + 'Path variables:\n'
            for name in context.paths:
                value = context.paths[name]
                s += prefix + Model.tab + name
                if value:
                    s += ': ' + value + '\n'
                else:
                    s += '\n'

        if context.dynamics_profiles:
            s += prefix + 'Dynamics profiles:\n'
            for name in context.dynamics_profiles:
                dynamics = context.dynamics_profiles[name]
                s += self.dynamics2str(dynamics, prefix + Model.tab*2)

        if context.event_in_ports:
            s += prefix + 'Event in ports:\n'
            for port in context.event_in_ports:
                s += prefix + Model.tab + port + '\n'

        if context.event_out_ports:
            s += prefix + 'Event out ports:\n'
            for port in context.event_in_ports:
                s += prefix + Model.tab + port + '\n'

        if context.structure:
            s += self.structure2str(context.structure, prefix)

        if context.simulation.runs or context.simulation.records or context.simulation.data_displays:
            s += self.simulation2str(context.simulation, prefix)
        
        return s
    
    def __str__(self):
        s = ''

        s += 'Targets:\n'
        for run in self.targets:
            s += Model.tab + run + '\n'
        
        s += 'Dimensions:\n'
        if self.dimensions != None:
            for d in self.dimensions:
                s += Model.tab + d + '\n'

        s += 'Units:\n'
        if self.units != None:
            for u in self.units:
                s += Model.tab + u + '\n'

        if self.context:
            s += 'Global context:\n'
            s += self.context2str(self.context, '')
            
        return s