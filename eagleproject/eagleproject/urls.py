"""eagleproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.views import static
from core import views as core_views
from notify import views as notify_views
from .settings import STATIC_ROOT

redirect_to_ousd_dapp = RedirectView.as_view(url='https://ousd.com/', permanent=True)

urlpatterns = [
    path("", core_views.dashboard),
    path("tx/debug/<slug:tx_hash>", core_views.tx_debug),
    path("backfill_internal_transactions", core_views.backfill_internal_transactions),
    path("reports", core_views.reports),
    path("reports/monthly/<int:year>/<int:month>", core_views.report_monthly, name='monthly'),
    path("reports/weekly/<int:year>/<int:week>", core_views.report_weekly, name='weekly'),
    path("reports/weekly", core_views.report_latest_weekly),
    path("reports/do-monthly", core_views.make_monthly_report),
    path("reports/do-weekly", core_views.make_weekly_report),
    path("reports/do-monthly/<int:year>/<int:month>", core_views.make_specific_month_report),
    path("reports/do-weekly/<int:year>/<int:week>", core_views.make_specific_week_report),
    path("reports/subscribe", core_views.subscribe, name='subscribe'),
    path("reports/confirm", core_views.confirm, name='confirm'),
    path("reports/unsubscribe", core_views.unsubscribe, name='unsubscribe'),
    #path("reports/test_email", core_views.test_email),
    path("apy", core_views.apr_index, name="apy"),
    path("apr", RedirectView.as_view(pattern_name="apy", permanent=True)),
    path("supply", core_views.supply),
    path("dripper", core_views.dripper),
    path("dune-analytics", core_views.dune_analytics),
    path("dashboards", core_views.public_dashboards),

    path("strategist", core_views.strategist),
    path("strategist/creator", core_views.strategist_creator),

    ## NOTE: These endpoints are deprecated in favor of scripts.
    ## Check `eagleproject/scripts` for the relevant scripts
    # path("reload", core_views.reload),
    # path("snap", core_views.take_snapshot),
    # path("fetch", core_views.fetch_transactions),
    # path("runtriggers", notify_views.run_triggers),
    # path("notifygc", notify_views.gc),

    path("api/v2/<slug:project>/speed_test", core_views.api_speed_test),

    # v2 views
    path("<slug:project>/address/<slug:address>", core_views.address, name="address"),

    # Redirects
    path("address/<slug:address>", RedirectView.as_view(url="/ousd/address/%(address)s", permanent=True)),

    # v2 API endpoints
    # TODO: Validate `project` param
    path("api/v2/<slug:project>/apr/trailing", core_views.api_apr_trailing),
    re_path(r'^api/v2/(?P<project>[\w-]+)/daily_stats/(?P<days>[0-9]{1,3})/$', core_views.api_daily_stats),
    re_path(r'^api/v2/(?P<project>[\w-]+)/daily_stats/(?P<days>[0-9]{1,3})/(?P<start>[0-9]{1,3})', core_views.api_daily_stats),
    re_path(r'^api/v2/(?P<project>[\w-]+)/apr/trailing/(?P<days>[0-9]{1,3})', core_views.api_apr_trailing_days),
    path("api/v2/<slug:project>/apr/history", core_views.api_apr_history),
    path("api/v2/<slug:project>/ratios", core_views.api_ratios),
    path("api/v2/<slug:project>/staking_stats", core_views.staking_stats),
    path("api/v2/<slug:project>/staking_stats_by_duration", core_views.staking_stats_by_duration),
    path("api/v2/<slug:project>/pools", core_views.coingecko_pools),
    path("api/v2/<slug:project>/address/<slug:address>/yield", core_views.api_address_yield, name="api_address_yield"),
    path("api/v2/<slug:project>/address/", core_views.api_address),
    path("api/v2/<slug:project>/address/<slug:address>/history", core_views.api_address_history, name="api_address_history"),
    path("api/v2/<slug:project>/tvl_history/<int:days>", core_views.tvl_history),
    path("api/v2/<slug:project>/strategies", core_views.strategies),
    path("api/v2/<slug:project>/collateral", core_views.collateral),
    path("api/v2/<slug:project>/apr/trailing_history/<int:days>", core_views.api_apr_trailing_history),
    path("api/v2/<slug:project>/dripper", core_views.api_dripper),

    # Deprecated v1 API endpoints (exists for backward compatibility)
    path("api/v1/apr/trailing", RedirectView.as_view(url="/api/v2/ousd/apr/trailing", permanent=True)),
    re_path(r'^api/v1/apr/trailing/(?P<days>[0-9]{1,3})', RedirectView.as_view(url="/api/v2/ousd/apr/trailing/%(days)s", permanent=True)),
    path("api/v1/apr/history", RedirectView.as_view(url="/api/v2/ousd/apr/history", permanent=True)),
    path("api/v1/ratios", RedirectView.as_view(url="/api/v2/ousd/ratios", permanent=True)),
    path("api/v1/staking_stats", RedirectView.as_view(url="/api/v2/ousd/staking_stats", permanent=True)),
    path("api/v1/staking_stats_by_duration", RedirectView.as_view(url="/api/v2/ousd/staking_stats_by_duration", permanent=True)),
    path("api/v1/pools", RedirectView.as_view(url="/api/v2/ousd/pools", permanent=True)),
    path("api/v1/address/<slug:address>/yield", RedirectView.as_view(url="/api/v2/ousd/address/%(address)s/yield", permanent=True)),
    path("api/v1/address/", RedirectView.as_view(url="/api/v2/ousd/address", permanent=True)),
    path("api/v1/address/<slug:address>/history", RedirectView.as_view(url="/api/v2/ousd/address/%(address)s/history", permanent=True)),
    path("api/v1/strategies", RedirectView.as_view(url="/api/v2/ousd/strategies", permanent=True)),
    path("api/v1/collateral", RedirectView.as_view(url="/api/v2/ousd/collateral", permanent=True)),
    path("api/v1/apr/trailing_history/<int:days>", RedirectView.as_view(url="/api/v2/ousd/apr/trailing_history/%(days)s", permanent=True)),

    # Retired URLS
    path("powermint", redirect_to_ousd_dapp),
    path("swap", redirect_to_ousd_dapp),
    path("flipper", redirect_to_ousd_dapp),
    
    # Static dir
    re_path(r'^static/(?P<path>.+)$', static.serve, {'document_root': STATIC_ROOT}),
]
