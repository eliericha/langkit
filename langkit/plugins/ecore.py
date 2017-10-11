from langkit.plugins import Plugin
from langkit.compiled_types import ASTNodeType, token_type
from jpype import startJVM, shutdownJVM, JPackage
from os.path import join

JARS_DIR = '/Users/richa/work/qgen-src/gms/' \
    'eclipse/com.adacore.xsd2ada/target/xsd2ada/lib'

JARS = (
    'org.eclipse.emf.common-2.12.0.v20160420-0247.jar',
    'org.eclipse.emf.ecore-2.12.0.v20160420-0247.jar',
    'org.eclipse.emf.ecore.xmi-2.12.0.v20160420-0247.jar'
)

cp_str = ':'.join(
    [join(JARS_DIR, jar) for jar in JARS])

startJVM(
    '/Library/Java/JavaVirtualMachines/jdk1.8.0_40.jdk/'
    'Contents/Home/jre/lib/server/libjvm.dylib',
    '-ea', '-Djava.class.path=%s' % cp_str)

org = JPackage('org')

# The EcoreFactory object through which we can instantiate Ecore objects
EF = org.eclipse.emf.ecore.EcoreFactory.eINSTANCE

# A utility class to construct file paths
URI = org.eclipse.emf.common.util.URI

# The resource class allowing to serialize models to XMI files
XMIResourceImpl = org.eclipse.emf.ecore.xmi.impl.XMIResourceImpl


class ConvertToEcore(Plugin):

    def __init__(self, disabled=False):
        super(ConvertToEcore, self).__init__(
            'convert AST to Ecore metamodel',
            disabled=disabled)

    def run(self, context):
        super(ConvertToEcore, self).run(context)

        # A dictionary keeping track of the Ecore equivalent of each langkit
        # concept we translate
        ast_to_ecore = {}

        epkg = ast_to_ecore[context] = EF.createEPackage()
        epkg.setName(str(context.lang_name))

        # I'm excluding list types because I can represent them with the
        # multiplicity attribute of EReferences (similar to langkit Fields)  in
        # Ecore
        class_node_types = [t for t in context.astnode_types
                            if not t.is_list_type]

        eclassifiers = epkg.getEClassifiers()

        token_type_eclass = ast_to_ecore[token_type] = EF.createEClass()
        token_type_eclass.setName('TokenType')
        eclassifiers.add(token_type_eclass)

        # Create all EClasses
        for t in class_node_types:
            eclass = ast_to_ecore[t] = EF.createEClass()
            eclassifiers.add(eclass)

            eclass.setName(str(t.name))
            eclass.setAbstract(t.abstract)

            if t.base():
                # The list is ordered so that t.base() occurs before t
                supertype = ast_to_ecore[t.base()]
                assert supertype
                eclass.getESuperTypes().add(supertype)

        # Create all EEnums.
        # TODO: extend to also handle node types that are is_enum_node
        for t in context.enum_types:
            eenum = ast_to_ecore[t] = EF.createEEnum()
            eclassifiers.add(eenum)

            eenum.setName(str(t.name))

            literals = eenum.getLiterals()
            for alt in t.alternatives:
                lit = ast_to_ecore[t] = EF.createEEnumLiteral()
                lit.setName(str(t.name))
                lit.setLiteral(str(t.name))
                literals.add(lit)

        # Second pass to create EReferences appropriately typed with the above
        # EClasses
        for t in class_node_types:
            public_fields = t.get_fields(
                include_inherited=False,
                predicate=lambda f: f.is_public)

            features = ast_to_ecore[t].getEStructuralFeatures()
            for field in public_fields:
                if field.type == token_type or \
                        isinstance(field.type, ASTNodeType):
                    feature = EF.createEReference()
                    if field.type.is_list_type:
                        feature.setEType(ast_to_ecore[field.type.element_type])
                        feature.setUpperBound(-1)
                    else:
                        feature.setEType(ast_to_ecore[field.type])
                else:
                    # TODO: translate types that are not ASTNodeType
                    feature = EF.createEAttribute()

                feature.setName(str(field.name))
                features.add(feature)

        # Serialize the result in an XMI file
        res = XMIResourceImpl(
            URI.createFileURI('%s.ecore' % context.lang_name))
        res.getContents().add(epkg)
        res.save(res.getDefaultSaveOptions())

        shutdownJVM()
