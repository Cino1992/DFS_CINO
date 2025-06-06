# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command for listing interconnect attachment groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import filter_rewrite
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties
from googlecloudsdk.core.resource import resource_projection_spec

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to list interconnect attachment groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To list interconnect attachment groups, run:

          $ {command}
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class List(base.ListCommand):
  """List interconnect attachment groups."""

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat("""
        table(
          name,
          attachments.flatten(show='keys', separator='\n'),
          intent.availabilitySla:label=INTENDED_SLA,
          configured.availabilitySla.effectiveSla:label=CONFIGURED_SLA
        )
    """)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())

    client = holder.client.apitools_client
    messages = client.MESSAGES_MODULE

    project = properties.VALUES.core.project.GetOrFail()

    display_info = args.GetDisplayInfo()
    defaults = resource_projection_spec.ProjectionSpec(
        symbols=display_info.transforms, aliases=display_info.aliases
    )
    args.filter, filter_expr = filter_rewrite.Rewriter().Rewrite(
        args.filter, defaults=defaults
    )
    request = messages.ComputeInterconnectAttachmentGroupsListRequest(
        project=project, filter=filter_expr
    )

    return list_pager.YieldFromList(
        client.interconnectAttachmentGroups,
        request,
        field='items',
        limit=args.limit,
        batch_size=None,
    )


List.detailed_help = DETAILED_HELP
