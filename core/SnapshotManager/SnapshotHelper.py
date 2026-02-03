from rest_framework.response import Response
from rest_framework import status
from api.Models.Snapshot.snapshot_daily_asset import SnapshotDailyAsset
from api.Models.Snapshot.snapshot_daily_location_cost import SnapshotDailyLocationCost
from api.Models.Snapshot.snapshot_daily_counts import SnapshotDailyCounts
from api.Models.Snapshot.snapshot_daily_location_counts import SnapshotDailyLocationCounts
from api.Models.Snapshot.snapshot_daily_currency import SnapshotDailyCurrency
from GSE_Backend.errors.ErrorDictionary import CustomError
import logging

class Logger():
    @staticmethod
    def getLogger():
        return logging.getLogger(__name__)


class SnapshotDailyFleetHelper():
    
    @staticmethod
    def fleet_snapshot_exists_for_daterange(start, end, db_name):
        return SnapshotDailyAsset.objects.using(db_name).filter(date_created__range=[start, end]).exists()

    @staticmethod
    def get_fleet_snapshots_in_daterange(start, end, db_name):
        return SnapshotDailyAsset.objects.using(db_name).filter(date_created__range=[start, end])


class SnapshotDailyCostHelper():
    
    @staticmethod
    def cost_snapshot_exists_for_daterange(start, end, db_name):
        return SnapshotDailyLocationCost.objects.using(db_name).filter(date_created__range=[start, end]).exists()

    @staticmethod
    def get_costs_snapshot_for_daterange(start, end, db_name):
        return SnapshotDailyLocationCost.objects.using(db_name).filter(date_created__range=[start, end])


class SnapshotDailyCountsHelper():

    @staticmethod
    def location_counts_snapshot_exists_for_daterange(start, end, db_name):
        return SnapshotDailyLocationCounts.objects.using(db_name).filter(date_of_checks__range=[start, end]).exists()

    @staticmethod
    def get_location_counts_snapshot_for_daterange(start, end, db_name):
        return SnapshotDailyLocationCounts.objects.using(db_name).filter(date_created__range=[start, end])

    @staticmethod
    def counts_snapshot_exists_for_daterange(start, end, db_name):
        return SnapshotDailyCounts.objects.using(db_name).filter(date_created__range=[start, end]).exists()

    @staticmethod
    def get_counts_snapshot_for_daterange(start, end, db_name):
        return SnapshotDailyCounts.objects.using(db_name).filter(date_created__range=[start, end])


class SnapshotDailyCurrencyHelper():
    
    @staticmethod
    def currency_snapshot_exists_for_daterange(start, end, db_name):
        return SnapshotDailyCurrency.objects.using(db_name).filter(date_modified__range=[start, end])

    @staticmethod
    def get_snapshot_currency(currency_code, db_name):
        return SnapshotDailyCurrency.objects.using(db_name).get(currency__code=currency_code)