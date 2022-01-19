"""Adapted from
sphinx.transforms.post_transforms.ReferencesResolver.resolve_anyref

If 'py' is one of the domains and `py:class` is defined,
the Python domain will be processed before the 'std' domain.

License for Sphinx
==================

Copyright (c) 2007-2019 by the Sphinx team (see AUTHORS file).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from contextlib import suppress

from docutils import nodes
from sphinx.transforms.post_transforms import ReferencesResolver


class CustomReferencesResolver(ReferencesResolver):

    def resolve_anyref(self, refdoc, node, contnode):
        """Resolve reference generated by the "any" role."""
        stddomain = self.env.get_domain('std')
        target = node['reftarget']

        # process 'py' domain first for python classes
        if "py:class" in node:
            with suppress(KeyError):
                py_domain = self.env.domains['py']
                py_ref = py_domain.resolve_any_xref(
                    self.env, refdoc, self.app.builder, target, node, contnode)
                if py_ref:
                    return self.create_node(py_ref[0])

        # resolve :term:
        term_ref = stddomain.resolve_xref(self.env, refdoc, self.app.builder,
                                          'term', target, node, contnode)
        if term_ref:
            # replace literal nodes with inline nodes
            if not isinstance(term_ref[0], nodes.inline):
                inline_node = nodes.inline(rawsource=term_ref[0].rawsource,
                                           classes=term_ref[0].get('classes'))
                if term_ref[0]:
                    inline_node.append(term_ref[0][0])
                term_ref[0] = inline_node
            return self.create_node(("std:term", term_ref))

        # next, do the standard domain
        std_ref = stddomain.resolve_any_xref(
            self.env, refdoc, self.app.builder, target, node, contnode)
        if std_ref:
            return self.create_node(std_ref[0])

        for domain in self.env.domains.values():
            try:
                ref = domain.resolve_any_xref(
                    self.env, refdoc, self.app.builder, target, node, contnode)
                if ref:
                    return self.create_node(ref[0])
            except NotImplementedError:
                # the domain doesn't yet support the new interface
                # we have to manually collect possible references (SLOW)
                for role in domain.roles:
                    res = domain.resolve_xref(self.env, refdoc,
                                              self.app.builder, role, target,
                                              node, contnode)
                    if res and isinstance(res[0], nodes.Element):
                        result = (f'{domain.name}:{role}', res)
                        return self.create_node(result)

        # no results considered to be <code>
        contnode['classes'] = []
        return contnode

    def create_node(self, result):
        res_role, newnode = result
        # Override "any" class with the actual role type to get the styling
        # approximately correct.
        res_domain = res_role.split(':')[0]
        if (len(newnode) > 0 and isinstance(newnode[0], nodes.Element)
                and newnode[0].get('classes')):
            newnode[0]['classes'].append(res_domain)
            newnode[0]['classes'].append(res_role.replace(':', '-'))
        return newnode


def setup(app):
    if (hasattr(app.registry, "get_post_transforms")
            and callable(app.registry.get_post_transforms)):
        post_transforms = app.registry.get_post_transforms()
    else:
        # Support sphinx 1.6.*
        post_transforms = app.post_transforms

    for i, transform_class in enumerate(post_transforms):
        if transform_class == ReferencesResolver:
            post_transforms[i] = CustomReferencesResolver
            break
    else:
        raise RuntimeError("ReferencesResolver not found")
