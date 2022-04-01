# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import proto  # type: ignore

from google.ads.googleads.v8.common.types import dates
from google.ads.googleads.v8.enums.types import keyword_plan_forecast_interval


__protobuf__ = proto.module(
    package="google.ads.googleads.v8.resources",
    marshal="google.ads.googleads.v8",
    manifest={"KeywordPlan", "KeywordPlanForecastPeriod",},
)


class KeywordPlan(proto.Message):
    r"""A Keyword Planner plan.
    Max number of saved keyword plans: 10000.
    It's possible to remove plans if limit is reached.

    Attributes:
        resource_name (str):
            Immutable. The resource name of the Keyword Planner plan.
            KeywordPlan resource names have the form:

            ``customers/{customer_id}/keywordPlans/{kp_plan_id}``
        id (int):
            Output only. The ID of the keyword plan.
        name (str):
            The name of the keyword plan.
            This field is required and should not be empty
            when creating new keyword plans.
        forecast_period (google.ads.googleads.v8.resources.types.KeywordPlanForecastPeriod):
            The date period used for forecasting the
            plan.
    """

    resource_name = proto.Field(proto.STRING, number=1,)
    id = proto.Field(proto.INT64, number=5, optional=True,)
    name = proto.Field(proto.STRING, number=6, optional=True,)
    forecast_period = proto.Field(
        proto.MESSAGE, number=4, message="KeywordPlanForecastPeriod",
    )


class KeywordPlanForecastPeriod(proto.Message):
    r"""The forecasting period associated with the keyword plan.
    Attributes:
        date_interval (google.ads.googleads.v8.enums.types.KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval):
            A future date range relative to the current
            date used for forecasting.
        date_range (google.ads.googleads.v8.common.types.DateRange):
            The custom date range used for forecasting.
            The start and end dates must be in the future.
            Otherwise, an error will be returned when the
            forecasting action is performed. The start and
            end dates are inclusive.
    """

    date_interval = proto.Field(
        proto.ENUM,
        number=1,
        oneof="interval",
        enum=keyword_plan_forecast_interval.KeywordPlanForecastIntervalEnum.KeywordPlanForecastInterval,
    )
    date_range = proto.Field(
        proto.MESSAGE, number=2, oneof="interval", message=dates.DateRange,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
